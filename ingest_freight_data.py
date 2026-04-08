import pandas as pd
import os
import pyodbc
from dotenv import load_dotenv
import re

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Dicionários de sinônimos para detecção automática de colunas
KEYWORDS = {
    'cep_init': ['CEP INICIAL', 'CEP INICIO', 'INICIO FAIXA', 'CEP INCIO', 'CEP START', 'CEP_INICIAL', 'CEP - INICIAL', 'CEP INÍCIO', 'INICIO', 'CEP_INICIO', 'CEP INIC', 'INIC'],
    'cep_final': ['CEP FINAL', 'FIM FAIXA', 'CEP END', 'CEP_FINAL', 'CEP - FINAL', 'FIM', 'CEP_FIM', 'FINAL'],
    'cidade': ['CIDADE', 'MUNICIPIO', 'DESTINO', 'LOCALIDADE', 'CIDADE DESTINO', 'CIDADE DE ATENDIMENTO', 'NOME CIDADE'],
    'uf': ['UF', 'ESTADO', 'EST', 'FEDERACAO', 'REGIAO'],
}

def clean_cep(cep):
    """Remove caracteres não numéricos e garante 8 dígitos."""
    if pd.isna(cep): return None
    # Converte para string e remove hifens/pontos
    cep_str = str(cep).replace('-', '').replace('.', '').replace(' ', '').split('.')[0]
    m = re.search(r'\d{5,8}', cep_str)
    if m:
        return m.group(0).zfill(8)[:8]
    return None

def get_db_connection():
    # EXPLICANDO: Verificamos quais variáveis estão faltando para ajudar no debug
    vars_to_check = ["DB_SERVER", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing = [v for v in vars_to_check if not os.environ.get(v)]
    
    if missing:
        print(f"⚠️ Erro: Variáveis de ambiente faltando: {', '.join(missing)}")
        print("Certifique-se de que o arquivo .env existe e contém essas chaves.")
        return None

    try:
        db_server = os.environ.get("DB_SERVER")
        db_name = os.environ.get("DB_NAME")
        db_user = os.environ.get("DB_USER")
        db_password = os.environ.get("DB_PASSWORD")
        
        # EXPLICANDO: Forçamos o driver ODBC 18 e o servidor via TCP
        conn_str = (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server=tcp:{db_server},1433;Database={db_name};Uid={db_user};Pwd={db_password};"
            f"Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
        )
        return pyodbc.connect(conn_str, autocommit=True)
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")
        return None

def detect_mapping(df_preview):
    """Tenta encontrar em qual linha estão os cabeçalhos e qual o índice das colunas."""
    # Percorre as primeiras 50 linhas
    for i in range(min(50, len(df_preview))):
        row = [str(val).upper() for val in df_preview.iloc[i].values]
        mapping = {}
        
        for key, synonyms in KEYWORDS.items():
            for syn in synonyms:
                if syn in row:
                    mapping[key] = row.index(syn)
                    break
        
        # Se achamos pelo menos as colunas essenciais de CEP
        if 'cep_init' in mapping and 'cep_final' in mapping:
            return i, mapping
            
    return None, None

def process_file(file_path, carrier_name):
    print(f"\n[ANALISANDO] {carrier_name} ({os.path.basename(file_path)})")
    
    try:
        # Carrega sem cabeçalho primeiro para detectar onde ele está
        # Se for .xls usa xlrd, se for .xlsx usa openpyxl
        engine = 'xlrd' if file_path.endswith('.xls') else 'openpyxl'
        
        # Tenta ler a aba correta (RTE usa ANEXO I, outros geralmente a 0)
        sheet_to_use = 'ANEXO I' if carrier_name == 'RTE' else 0
        df_preview = pd.read_excel(file_path, sheet_name=sheet_to_use, header=None, engine=engine)
        
        header_idx, mapping = detect_mapping(df_preview)
        
        if header_idx is None:
            print(f"[-] Nao foi possivel identificar as colunas de CEP em {carrier_name}.")
            return None
            
        # Re-carrega os dados a partir do cabeçalho encontrado
        df = pd.read_excel(file_path, sheet_name=sheet_to_use, header=header_idx + 1, engine=engine)
        
        # Mapeia as colunas detectadas
        # Usamos iloc com os índices que o mapping nos deu
        final_df = pd.DataFrame()
        final_df['cepInicial'] = df_preview.iloc[header_idx+1:, mapping['cep_init']].apply(clean_cep)
        final_df['cepFinal'] = df_preview.iloc[header_idx+1:, mapping['cep_final']].apply(clean_cep)
        
        # Cidade e UF podem ser opcionais se não encontradas
        final_df['Cidade'] = df_preview.iloc[header_idx+1:, mapping['cidade']].astype(str).str.upper() if 'cidade' in mapping else 'N/A'
        final_df['UF'] = df_preview.iloc[header_idx+1:, mapping['uf']].astype(str).str.upper() if 'uf' in mapping else 'N/A'
        final_df['Transportador'] = carrier_name
        
        # Limpeza final
        final_df = final_df.dropna(subset=['cepInicial', 'cepFinal'])
        # Garante que não há lixo (ex: linhas de texto no meio dos CEPs)
        final_df = final_df[final_df['cepInicial'].str.isdigit() == True]
        
        print(f"[+] Sucesso! {len(final_df)} linhas identificadas.")
        return final_df
        
    except Exception as e:
        print(f"[-] Erro ao processar {carrier_name}: {e}")
        return None

def sync_to_sql(df_total):
    conn = get_db_connection()
    if conn is None: return
    
    cursor = conn.cursor()
    try:
        for carrier in df_total['Transportador'].unique():
            print(f"[LIMPANDO] Dados antigos de {carrier}...")
            cursor.execute("DELETE FROM TransportTable WHERE Transportador = ?", carrier)
        
        print(f"[ENVIANDO] {len(df_total)} linhas para o SQL Server...")
        insert_query = "INSERT INTO TransportTable (CepInicial, CepFinal, Cidade, UF, Transportador) VALUES (?, ?, ?, ?, ?)"
        data_to_insert = [tuple(x) for x in df_total[['cepInicial', 'cepFinal', 'Cidade', 'UF', 'Transportador']].values]
        
        cursor.fast_executemany = True
        cursor.executemany(insert_query, data_to_insert)
        print("[OK] Sincronizacao concluida com sucesso!")
        
    except Exception as e:
        print(f"[-] Erro durante a insercao no SQL: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    folder_path = 'TabelasTransportadoras'
    all_data = []
    
    # Mapeamento simples de arquivos para nomes de transportadoras
    FILE_RULES = {
        'TERMACO': r'TERMACO',
        'GOLLOG': r'GOLLOG',
        'EXCARGO': r'\(Exc\)',
        'RTE': r'RTE'
    }
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if not filename.endswith(('.xlsx', '.xls')): continue
        
        identified_carrier = None
        for carrier, pattern in FILE_RULES.items():
            if re.search(pattern, filename, re.IGNORECASE):
                identified_carrier = carrier
                break
        
        if identified_carrier:
            df = process_file(file_path, identified_carrier)
            if df is not None and not df.empty:
                all_data.append(df)
        else:
            if 'CORREIOS' not in filename.upper():
                print(f"[*] Arquivo ignorado: {filename}")
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        sync_to_sql(final_df)
    else:
        print("[!] Nenhum dado valido encontrado para importacao.")
