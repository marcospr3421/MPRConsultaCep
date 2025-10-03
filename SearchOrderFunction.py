import os
import requests
import pyodbc
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QDialog, QMessageBox
    
class ResultWindow(QDialog):
    """A dialog window to display order search results."""
    def __init__(self, results):
        """
        Initializes the ResultWindow.

        Args:
            results (list): A list of tuples, where each tuple contains
                            the destination CEP for an order.
        """
        super().__init__()
        self.setWindowTitle("Search Results")
        layout = QVBoxLayout()

        if results:
            for result in results:
                line = f"CepDest: {result[0]}"
                result_label = QLabel(line)  # Create label for each result
                layout.addWidget(result_label)
        else:
             layout.addWidget(QLabel("No results found.")) # Clear message if no results

        self.setLayout(layout)

    
def search_order(self,main_window):
    """
    Searches for an order by its number and displays the results.

    This function is triggered by the user interface. It retrieves the order
    number from the input field, connects to the SQL Server database using
    credentials stored in environment variables, and queries the
    `PedidosDisponiveis` table.

    The database password must be provided via the `DB_PASSWORD`
    environment variable.

    Args:
        self: The instance of the calling class (typically the main window).
        main_window: The main application window instance, used to access the
                     order input field.

    Returns:
        list | None: A list of database rows (as tuples) if the order is
                     found. Returns None if no results are found or if a
                     database or configuration error occurs.
    """
    order = main_window.order_input.text()
    order = order.zfill(8)

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

        # Execute the SQL query to retrieve the transport information based on the order
        cursor.execute("SELECT DestCep FROM PedidosDisponiveis WHERE NumeroDoPedido = ?", order)
        results = cursor.fetchall()

        conn.close()

        if results:
            self.result_window = ResultWindow(results) # Create dialog
            self.result_window.exec() # Show dialog
        else:
            QMessageBox.information(self, "Information", "Order not found.") # Use message box for simple info

        return results
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        QMessageBox.critical(self, "Database Error", f"A database error occurred:\n\n{sqlstate}\n\nPlease check your credentials and network connection.")
        return None
