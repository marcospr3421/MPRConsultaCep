# MPRConsultaCep Development Guide

## Commands
- Run web app (production code, deployed on Railway): `python app.py`
- Run legacy desktop app (PyQt6): `python MprConsultaCep.py`
- Import/update one carrier (dry-run; add `--apply` to write): `python ingest_carrier.py --carrier GLM --file "TabelasTransportadoras/<planilha>.xlsx"`
- Remove one carrier (dry-run; add `--apply`): `python ingest_carrier.py --carrier "GOL LOG" --remove`
- Reimport all carrier spreadsheets (no dry-run/backup): `python ingest_freight_data.py`
- Package with PyInstaller: `pyinstaller --onefile --windowed --icon=22994_boat_icon.ico MprConsultaCep.py`
- Test Correios API: `python testeCep.py`
- Test CEP search: `python SearchCepFunction.py`

## Code Style Guidelines
- **Imports**: System libraries first, third-party packages second, local modules last
- **Formatting**: 4-space indentation, max line length ~100 chars
- **Docstrings**: Use triple quotes for function documentation with Args/Returns sections
- **UI Components**: PyQt6 with consistent stylesheet defined in MainWindow
- **Error Handling**: Use try/except with specific exception types and user-friendly messages
- **Database**: Use pyodbc for SQL Server connections with proper connection closing
- **Function Naming**: snake_case for functions (e.g., `search_cep`, `consultar_cep`)
- **Class Naming**: PascalCase for classes (e.g., `MainWindow`, `ResultWindow`)
- **API Calls**: Use requests library with raise_for_status() and proper response validation
- **Security**: Store sensitive data (tokens, credentials) in environment variables, not code
- **Input Validation**: Validate user input before processing (use validators for UI fields)

## Project Structure
- `app.py`: Flask web app (CEP/order search, carrier rules, `/health`) — this is what runs in production
- `templates/`, `static/`: Web UI
- `config/carrier_rules.json`: Per-carrier blocking rules (`max_weight_kg`, `max_length_cm`, `max_item_sum_dims_cm`, `forbidden_categories`)
- `ingest_freight_data.py`: Spreadsheet parsing (column auto-detection, `FILE_RULES`, `ALIASES`, `SHEET_BY_CARRIER`, `DEFAULT_UF_BY_CARRIER`)
- `ingest_carrier.py`: Safe single-carrier import/removal into `TransportTable` (dry-run, CSV backup, transaction)
- `TabelasTransportadoras/`: Carrier coverage spreadsheets (GLM proposal is NOT versioned — contains prices)
- `MprConsultaCep.py`: Legacy desktop application and UI setup
- `SearchCepFunction.py`: Postal code lookup against database
- `SearchOrderFunction.py`: Order lookup in database
- `testeCep.py`: Correios API integration for address lookups
- `InsertFunction.py`: Utility for database data insertion

## Carriers & Data
- Active carriers: CORREIOS (via API), GLM, RODONAVES (file prefix `RTE`), TERMACO, EXCARGO. GOL LOG was discontinued (2026-10-05).
- Coverage lives in Azure SQL table `TransportTable` (`CepInicial`, `CepFinal`, `Cidade`, `UF`, `Transportador`).
- When a spreadsheet has two `UF` columns (origin/destination), the one after the city column is used.
- Always run `ingest_carrier.py` without `--apply` first and check row counts/UFs before writing.
- `mprsqlserver` firewall only allows Railway static IPs; local ingestion requires temporarily allowing the client IP.

## Deploy
- Railway auto-deploys every merge to `main` (Dockerfile). URL: https://mprconsultacep-production.up.railway.app (`/health`).
