"""
Ingestao de UMA transportadora na TransportTable, com dry-run, backup e transacao.

Diferente de `ingest_freight_data.py` (que reimporta todas as planilhas da pasta),
este script mexe apenas nas linhas da transportadora informada:
  1. Le e valida a planilha (mesma deteccao de colunas do ingest_freight_data).
  2. Faz backup em CSV das linhas atuais da transportadora no banco.
  3. Em UMA transacao: DELETE das linhas antigas + INSERT das novas.
  4. Valida contagem e um CEP de amostra; se divergir, faz ROLLBACK.

Sem --apply roda em modo dry-run (nao grava nada no banco).

Autor: Marcos Ribeiro (marcospr3421)
Versao: 1.0
Requisitos: .env com DB_SERVER/DB_NAME/DB_USER/DB_PASSWORD, ODBC Driver 18,
            IP liberado no firewall do Azure SQL.
"""
import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyodbc

import ingest_freight_data as ingest

LOG_DIR = Path("logs")
BACKUP_DIR = Path("backups")


def setup_logging(carrier):
    """Configura log em console e em logs/ingest_<carrier>_<data>.log."""
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / f"ingest_{carrier}_{datetime.now():%Y-%m-%d}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(log_file, encoding="utf-8")],
    )
    return logging.getLogger("ingest_carrier")


def get_transactional_connection():
    """Abre conexao com autocommit desligado para DELETE+INSERT atomico.

    Returns:
        pyodbc.Connection: Conexao aberta.

    Raises:
        RuntimeError: Se faltar alguma variavel de ambiente.
    """
    required = ["DB_SERVER", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        raise RuntimeError(f"Variaveis de ambiente faltando: {', '.join(missing)}")

    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server=tcp:{os.environ['DB_SERVER']},1433;Database={os.environ['DB_NAME']};"
        f"Uid={os.environ['DB_USER']};Pwd={os.environ['DB_PASSWORD']};"
        "Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str, autocommit=False)


def main():
    parser = argparse.ArgumentParser(description="Ingestao de uma transportadora na TransportTable")
    parser.add_argument("--carrier", required=True, help="Nome da transportadora (ex: GLM)")
    parser.add_argument("--file", required=True, help="Caminho da planilha")
    parser.add_argument("--apply", action="store_true", help="Grava no banco (sem isso: dry-run)")
    args = parser.parse_args()

    log = setup_logging(args.carrier)
    db_name = ingest.ALIASES.get(args.carrier, args.carrier)
    names_to_replace = ingest.CLEANUP_GROUPS.get(db_name, [db_name])

    # 1. Leitura e validacao da planilha
    if not Path(args.file).is_file():
        log.error(f"Arquivo nao encontrado: {args.file}")
        return 1
    df = ingest.process_file(args.file, args.carrier)
    if df is None or df.empty:
        log.error("Nenhuma linha valida na planilha. Abortando sem tocar no banco.")
        return 1
    df["Transportador"] = db_name
    invalid = (df["cepInicial"] > df["cepFinal"]).sum()
    if invalid:
        log.error(f"{invalid} faixas com CEP inicial maior que o final. Abortando.")
        return 1
    sample_cep = df.iloc[len(df) // 2]["cepInicial"]
    log.info(f"Planilha OK: {len(df)} faixas para '{db_name}' (substitui: {names_to_replace})")

    try:
        conn = get_transactional_connection()
    except (RuntimeError, pyodbc.Error) as e:
        log.error(f"Falha ao conectar no banco: {e}")
        return 1

    try:
        cursor = conn.cursor()
        placeholders = ", ".join("?" for _ in names_to_replace)

        # 2. Backup das linhas atuais
        current = pd.read_sql(
            f"SELECT CepInicial, CepFinal, Cidade, UF, Transportador FROM TransportTable "
            f"WHERE Transportador IN ({placeholders})",
            conn, params=names_to_replace,
        )
        if not current.empty:
            BACKUP_DIR.mkdir(exist_ok=True)
            backup_file = BACKUP_DIR / f"TransportTable_{db_name}_{datetime.now():%Y%m%d_%H%M%S}.csv"
            current.to_csv(backup_file, index=False, encoding="utf-8")
            log.info(f"Backup de {len(current)} linhas atuais em {backup_file}")
        else:
            log.info("Nenhuma linha atual no banco para esta transportadora (primeira carga).")

        if not args.apply:
            log.info(f"[DRY-RUN] Apagaria {len(current)} e inseriria {len(df)} linhas. "
                     "Rode com --apply para gravar.")
            return 0

        # 3. DELETE + INSERT na mesma transacao
        cursor.execute(f"DELETE FROM TransportTable WHERE Transportador IN ({placeholders})",
                       names_to_replace)
        log.info(f"Removidas {cursor.rowcount} linhas antigas")
        cursor.fast_executemany = True
        cursor.executemany(
            "INSERT INTO TransportTable (CepInicial, CepFinal, Cidade, UF, Transportador) "
            "VALUES (?, ?, ?, ?, ?)",
            [tuple(r) for r in df[["cepInicial", "cepFinal", "Cidade", "UF", "Transportador"]].values],
        )

        # 4. Validacao antes do commit
        cursor.execute("SELECT COUNT(*) FROM TransportTable WHERE Transportador = ?", db_name)
        count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM TransportTable WHERE ? BETWEEN CepInicial AND CepFinal "
                       "AND Transportador = ?", (sample_cep, db_name))
        hit = cursor.fetchone()[0]
        if count != len(df) or hit == 0:
            conn.rollback()
            log.error(f"Validacao falhou (contagem {count}/{len(df)}, amostra {sample_cep}: {hit}). "
                      "ROLLBACK executado, banco inalterado.")
            return 1

        conn.commit()
        log.info(f"[OK] COMMIT: {count} faixas de '{db_name}' gravadas. "
                 f"CEP de amostra {sample_cep} encontrado.")
        return 0

    except (pyodbc.Error, pd.errors.DatabaseError) as e:
        conn.rollback()
        log.error(f"Erro no banco, ROLLBACK executado: {e}")
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())

# Uso:
#   python ingest_carrier.py --carrier GLM --file "TabelasTransportadoras/GLM - Proposta Comercial AZ 28.04.xlsx"
#   python ingest_carrier.py --carrier GLM --file "TabelasTransportadoras/GLM - Proposta Comercial AZ 28.04.xlsx" --apply
#
# Rollback manual (se precisar remover a GLM depois do commit):
#   DELETE FROM TransportTable WHERE Transportador = 'GLM';
#   (ou reimportar o CSV salvo em backups/)
