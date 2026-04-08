# MPRConsultaCep Development Guide

## Commands
- Run application: `python MprConsultaCep.py`
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
- `MprConsultaCep.py`: Main application and UI setup
- `SearchCepFunction.py`: Postal code lookup against database
- `SearchOrderFunction.py`: Order lookup in database
- `testeCep.py`: Correios API integration for address lookups
- `InsertFunction.py`: Utility for database data insertion