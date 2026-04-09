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

## 👨‍💻 Feito por:
**Marcos Ribeiro | MPR Labs**  
Desenvolvido com o apoio de IA mentoria técnica Avançada (V6.4 Master Plus Edition).