import os
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QDialog, QMessageBox, QGridLayout
    
class ResultWindow(QDialog):
    """A dialog window to display CEP search results in a grid."""
    def __init__(self, results):
        """
        Initializes the ResultWindow.

        Args:
            results (list): A list of tuples, where each tuple contains
                            database query results for a carrier.
        """
        super().__init__()
        self.setWindowTitle("Search Results")
        layout = QGridLayout()
        row = 0

        if results:
            for result in results:
                cidade_label = QLabel(f"Cidade: {result[3]}")
                uf_label = QLabel(f"UF: {result[4]}")
                transporte_label = QLabel(f"Transporte: {result[5]}")

                cidade_label.setStyleSheet("font-size: 14px;")
                uf_label.setStyleSheet("font-size: 14px;")
                transporte_label.setStyleSheet("font-size: 14px;")

                layout.addWidget(cidade_label, row, 0)
                layout.addWidget(uf_label, row, 1)
                layout.addWidget(transporte_label, row, 2)
                row +=1
        else:
            no_results_label = QLabel("No results found.")
            no_results_label.setStyleSheet("font-size: 14px;")
            layout.addWidget(no_results_label, 0, 0)

        self.setLayout(layout)


    
def search_cep_db_logic(cep):
    """
    Performs the database query for a CEP.
    Returns (results, error_msg)
    """
    try:
        cep = cep.strip().zfill(8)
        db_password = os.environ.get("DB_PASSWORD")
        if not db_password:
            return None, "Database password not found."

        db_server = os.environ.get("DB_SERVER", "mprsqlserver.database.windows.net")
        db_name = os.environ.get("DB_NAME", "mprDB02")
        db_user = os.environ.get("DB_USER", "azureuser")
        conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:{db_server},1433;Database={db_name};Uid={db_user};Pwd={db_password};Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TransportTable WHERE ? BETWEEN CepInicial AND CepFinal order by Transportador ASC", cep)
        results = cursor.fetchall()
        conn.close()
        return results, None
    except pyodbc.Error as ex:
        try:
            sqlstate = ex.args[0]
            error_msg = ex.args[1] if len(ex.args) > 1 else str(ex)
        except Exception:
            sqlstate = "Unknown"
            error_msg = str(ex)
        return None, f"Database Error (State: {sqlstate}): {error_msg}"
    except Exception as e:
        return None, f"Unexpected Error: {str(e)}"

def search_cep(self, main_window):
    """
    Legacy search_cep function updated to use the new logic for synchronous calls.
    (Keeping signature for compatibility if called directly).
    """
    cep = main_window.cep_input.text()
    results, error = search_cep_db_logic(cep)
    
    if error:
        QMessageBox.critical(self, "Database Error", f"A database error occurred:\n\n{error}\n\nPlease check your credentials and network connection.")
        return None
        
    if results:
        self.result_window = ResultWindow(results)
        self.result_window.exec()
    else:
        QMessageBox.information(self, "Information", "CEP not found.")
    return results
