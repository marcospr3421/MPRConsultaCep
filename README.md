# API Fretes AZ - Inteligência Logística 🚀

Um sistema web inteligente projetado para ajudar os colaboradores da AZ Acessórios a escolherem a transportadora ideal de maneira rápida, visual e livre de erros.

O sistema faz o diagnóstico completo do frete com base:
1. Em um **CEP** (busca simples para viabilidade).
2. Em um **Número de Pedido** (busca inteligente com *Raio-X* logístico).

---

## 🌟 Funcionalidades Principais (V6.4)

- **Integração com ERP / SQL:** Busca dados validados do cliente, valor do pedido, canal de venda e detalhes completos.
- **Painel de Itens:** Exibe na tela todos os SKUs do pedido informando suas dimensões e preços.
- **Cubagem Inteligente Padrão Indústria:** Calcula internamente se o **Peso Físico** ou **Peso Cubado (Volumétrico)** é o maior e aplica a regra tarifária correta de envio.
- **Alerta de Categoria Crítica (`BIG`):** Alerta imediatamente o colaborador e bloqueia envio por Correios caso o produto se enquadre em regras extragrandes.
- **Resiliência de Dados (API vs DB):**
   - Na descoberta do CEP, prioriza consultar o serviço da API do ViaCEP/Correios para dados fresquinhos (Bairro/Cidade atualizada).
   - Se a API cair, o sistema assume os dados originais contidos no seu Banco de Dados como redundância (Failover).
- **Interface Premium e Glassmorphism:** Cores que respondem contextualmente (Bloqueado/Recomendado) focadas 100% em legibilidade.

---

## ⚙️ Arquitetura e Engenharia Backend

O núcleo funcional é feito em `Python` sob a engrenagem web do `Flask`. Conecta via ODBC para o Azure SQL Database.

### Camada de Regras Dinâmicas
As regras de trava de Frete não estão hard-coded. Tudo é guiado por um arquivo JSON simples listado em `config/carrier_rules.json`.

Exemplo de configuração dinâmica:
```json
{
  "CORREIOS": {
    "max_weight_kg": 30,
    "max_length_cm": 100,
    "forbidden_categories": ["BIG", "GIGANTE"]
  }
}
```
*Isto permite a qualquer admin expandir regras logísticas para novas transportadoras futuramente, editando um simples pedaço de texto.*

Chaves aceitas por transportadora:

| Chave | Bloqueia quando |
|---|---|
| `max_weight_kg` | Peso de cobrança (maior entre real e cubado) excede o limite |
| `max_length_cm` | Maior dimensão de qualquer item excede o limite |
| `max_item_sum_dims_cm` | Soma C+L+A do maior item excede o limite (hoje só GLM) |
| `forbidden_categories` | Pedido tem item BIG/GIGANTE e a lista não está vazia |

> `max_sum_dims_cm` e `extra_fee_threshold_cm` existem no JSON mas **não são validados** pelo app.

---

## 🚚 Transportadoras Ativas

| Transportadora | Fonte da cobertura | Regra de bloqueio (`carrier_rules.json`) |
|---|---|---|
| **CORREIOS** | API dos Correios (prioridade) + fallback no banco | 30 kg, 100 cm, bloqueia BIG |
| **GLM** | Planilha da proposta comercial (aba `Abrangência`) | 50 kg, 170 cm, soma 240 cm, aceita BIG |
| **RODONAVES** | Planilha `RTE - ...` (aba `ANEXO I`) | 500 kg, 300 cm |
| **TERMACO** | Planilha `TERMACO ...` | 500 kg, 300 cm |
| **EXCARGO** | Planilha `(Exc) ...` (só SP, UF fixa) | 1000 kg, 500 cm |

**GOL LOG** foi descontinuada em 2026-10-05 (removida do banco, das regras e da ingestão).

A cobertura por CEP vem da tabela `TransportTable` (`CepInicial`, `CepFinal`, `Cidade`, `UF`, `Transportador`) no Azure SQL.

---

## 📥 Manutenção das Tabelas de Transportadoras

Use `ingest_carrier.py` para importar, atualizar ou remover **uma** transportadora sem tocar nas demais.
Ele roda em **dry-run** por padrão, salva backup CSV em `backups/` antes de alterar e grava tudo em
**uma transação** (com validação e `ROLLBACK` automático se algo divergir).

```powershell
# Pré-requisitos: .venv ativo, ODBC Driver 18, e credenciais na sessão
$env:DB_SERVER="mprsqlserver.database.windows.net"; $env:DB_NAME="mprDB02"; $env:DB_USER="azureuser"
$env:DB_PASSWORD=[System.Net.NetworkCredential]::new("", (Read-Host "Senha" -AsSecureString)).Password

# Importar/atualizar (dry-run, depois --apply)
python ingest_carrier.py --carrier GLM --file "TabelasTransportadoras\GLM - Proposta Comercial AZ 28.04.xlsx"
python ingest_carrier.py --carrier GLM --file "TabelasTransportadoras\GLM - Proposta Comercial AZ 28.04.xlsx" --apply

# Remover uma transportadora
python ingest_carrier.py --carrier "GOL LOG" --remove
python ingest_carrier.py --carrier "GOL LOG" --remove --apply
```

Para os nomes de `--carrier` (RTE, EXCARGO, TERMACO, GLM) e a aba/UF de cada planilha, veja
`FILE_RULES`, `ALIASES`, `SHEET_BY_CARRIER` e `DEFAULT_UF_BY_CARRIER` em `ingest_freight_data.py`.
`python ingest_freight_data.py` reimporta **todas** as planilhas da pasta de uma vez (sem dry-run/backup).

**Nova transportadora:** coloque a planilha em `TabelasTransportadoras/`, adicione o nome em `FILE_RULES`
(e em `SHEET_BY_CARRIER` se as faixas não estiverem na primeira aba), rode o dry-run e confira as UFs.
Depois adicione a regra em `config/carrier_rules.json`.

> A proposta comercial da GLM contém preços e **não** é versionada; mantenha a planilha só localmente.
> O firewall do `mprsqlserver` aceita apenas os IPs do Railway: libere temporariamente o seu IP no
> portal do Azure (SQL Server → Networking) para rodar a ingestão e remova a regra depois.

---

## 🚢 Deploy

O Railway (projeto `MPR-ConsultaCep`, ambiente `production`) faz **deploy automático a cada merge na `main`**
via GitHub, usando o `Dockerfile`. URL: https://mprconsultacep-production.up.railway.app — saúde em `/health`.
Rollback: Railway → Deployments → deploy anterior → Redeploy.

---

## 🛠️ Stack Tecnológica

| Componente | Tecnologia |
|---|---|
| **Backend** | Python 3 + Flask |
| **Banco de Dados** | Microsoft Azure SQL |
| **Driver de Conexão** | `pyodbc` (ODBC Driver 18 for SQL Server) |
| **Frontend** | HTML5, CSS3, ES6 Javascript |
| **Hospedagem / CI/CD** | Railway App + GitHub |

---

## 🚀 Como Rodar Localmente (Desenvolvimento)

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/marcospr3421/MPRConsultaCep.git
   cd MPRConsultaCep
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as Variáveis de Ambiente:**
   Crie um arquivo `.env` na raiz do projeto com as credenciais do seu banco:
   ```env
   DB_SERVER=nome_do_servidor.database.windows.net
   DB_NAME=seu_banco
   DB_USER=seu_usuario
   DB_PASSWORD=sua_senha
   ```

5. **Execute a aplicação:**
   ```bash
   python app.py
   ```
   Acesse no navegador: `http://localhost:5000`

---

## 📝 Histórico de Mudanças

### 2026-10-05
- **GLM adicionada**: 15.043 faixas de CEP importadas da proposta comercial; regra de bloqueio 50 kg / 170 cm / soma 240 cm (PR #3).
- **`ingest_carrier.py`**: ingestão/remoção de uma transportadora com dry-run, backup e transação (PRs #4, #5).
- **GOL LOG removida**: 9.105 faixas apagadas do banco (backup CSV local) e removida do código (PR #5).
- **UF corrigida**: RODONAVES usava a UF de origem (sempre SP); EXCARGO gravava a região como UF. Ambas reimportadas (PR #6).

---

## 👨‍💻 Feito por:
**Marcos Ribeiro | MPR Labs**  
Desenvolvido com o apoio de IA mentoria técnica Avançada (V6.4 Master Plus Edition).

## Networking - Railway Static Outbound IPs (HA)

> Migrado de Legacy para HA Static IPs em 2026-07-20 (Linear MPR-749).

Trafego de saida deste servico usa os IPs estaticos (SFO): 152.55.176.240, 152.55.177.181, 162.220.232.250

Allowlists que DEVEM conter esses IPs:

- Azure SQL `mprsqlserver` - regras `Railway-HA-1..5`
- Key Vault `MprKv2024Az` - network rules (defaultAction: Deny)

ATENCAO: se os IPs mudarem (Railway > Settings > Networking), atualizar as allowlists ANTES do redeploy. Runbook: infra-backups/2026-07-20-railway-ha.
