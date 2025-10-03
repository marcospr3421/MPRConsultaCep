import os
import pyodbc
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


    
def search_cep(self,main_window):
    """
    Searches for a carrier by CEP and displays the results.

    This function is triggered by the user interface. It retrieves the CEP
    from the input field, connects to the SQL Server database using
    credentials stored in environment variables, and queries the
    `TransportTable`.

    The database password must be provided via the `DB_PASSWORD`
    environment variable.

    Args:
        self: The instance of the calling class (typically the main window).
        main_window: The main application window instance, used to access the
                     CEP input field.

    Returns:
        list | None: A list of database rows (as tuples) if carriers are
                     found for the CEP. Returns None if no results are
                     found or if a database or configuration error occurs.
    """
    cep = main_window.cep_input.text()
    cep = cep.zfill(8)
    
    # Connect to your SQL Server database
    # NOTE: The database password should be set as an environment variable
    # named `DB_PASSWORD` for security.
    db_password = os.environ.get("DB_PASSWORD")
    if not db_password:
        QMessageBox.critical(self, "Configuration Error", "Database password not found. Please set the DB_PASSWORD environment variable.")
        return

    conn_str = f"Driver={{SQL Server}};Server=tcp:mprsqlserver.database.windows.net,1433;Database=mprDB02;Uid=azureuser;Pwd={db_password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Using a parameterized query to prevent SQL injection
        cursor.execute("SELECT * FROM TransportTable WHERE ? BETWEEN CepInicial AND CepFinal order by Transportador ASC", cep)
        results = cursor.fetchall()

        conn.close()

        if results:
            self.result_window = ResultWindow(results) # Create dialog
            self.result_window.exec() # Show dialog
        else:
            QMessageBox.information(self, "Information", "CEP not found.") # Use message box for simple info

        return results
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        QMessageBox.critical(self, "Database Error", f"A database error occurred:\n\n{sqlstate}\n\nPlease check your credentials and network connection.")
        return None
