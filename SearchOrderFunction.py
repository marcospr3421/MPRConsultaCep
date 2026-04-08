import os
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QDialog, QMessageBox
from PyQt6.QtCore import Qt
    
class ResultWindow(QDialog):
    """A dialog window to display order search results."""
    def __init__(self, results):
        """
        Initializes the ResultWindow.

        Args:
            results (list): A list of tuples, where each tuple contains
                            order details.
        """
        super().__init__()
        self.setWindowTitle("Detalhes do Pedido")
        layout = QVBoxLayout()
        
        # Style for the labels to look like the rest of the app
        label_style = "background-color: black; font-family: monospace; font-size: 16px; color: white; padding: 5px;"

        if results and len(results) > 0:
            # Assuming the order of columns from the query:
            # DestCep (0), Transportadora (1), ServicoEntrega (2), Canal (3), DestMunicipio (4), DestEstado (5), NomeProduto (6), DataVenda (7), ValorPedido (8)
            r = results[0]
            
            # Helper to handle None values gracefully
            def safe_str(val):
                return str(val) if val is not None else "N/A"

            fields = [
                f"CEP Destino: {safe_str(r[0])}",
                f"Transportadora: {safe_str(r[1])}",
                f"Serviço: {safe_str(r[2])}",
                f"Canal: {safe_str(r[3])}",
                f"Local: {safe_str(r[4])} - {safe_str(r[5])}",
                f"Produto: {safe_str(r[6])}",
                f"Data Venda: {safe_str(r[7])}",
                f"Valor: R$ {safe_str(r[8])}"
            ]

            for field_text in fields:
                label = QLabel(field_text)
                label.setStyleSheet(label_style)
                label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                layout.addWidget(label)
        else:
             layout.addWidget(QLabel("No results found.")) 

        self.setLayout(layout)

    
def search_order_db_logic(order):
    """
    Performs the database query for an order.
    Returns (results, error_msg)
    """
    try:
        order = order.strip()
        if len(order) > 0 and len(order) < 8:
            order = order.zfill(8)

        db_password = os.environ.get("DB_PASSWORD")
        if not db_password:
            return None, "Database password not found."

        db_server = os.environ.get("DB_SERVER", "mprsqlserver.database.windows.net")
        db_name = os.environ.get("DB_NAME", "mprDB02")
        db_user = os.environ.get("DB_USER", "azureuser")
        import pyodbc
        import time
        conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:{db_server},1433;Database={db_name};Uid={db_user};Pwd={db_password};Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"

        start_time = time.time()
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        
        print(f"DEBUG: Executing query for Order: {order}")
        # Use TOP 1 to speed up scan on 2M+ rows
        query = """
            SELECT TOP 1 
                DestCep, Transportadora, ServicoEntrega, Canal, 
                DestMunicipio, DestEstado, NomeProduto, DataVenda, ValorPedido 
            FROM PedidosDisponiveis 
            WHERE NumeroDoPedido = ?
        """
        cursor.execute(query, order)
        results = cursor.fetchall()
        execution_time = time.time() - start_time
        print(f"DEBUG: Query finished in {execution_time:.2f} seconds. Found {len(results)} results.")
        
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

def search_order(self, main_window):
    """
    Legacy search_order function updated to use the new logic for synchronous calls.
    (Keeping signature for compatibility if called directly).
    """
    order = main_window.order_input.text()
    results, error = search_order_db_logic(order)

    if error:
        QMessageBox.critical(self, "Database Error", f"A database error occurred:\n\n{error}\n\nPlease check your credentials and network connection.")
        return None

    if results:
        self.result_window = ResultWindow(results)
        self.result_window.exec()
    else:
        QMessageBox.information(self, "Information", "Order not found.")
    return results
