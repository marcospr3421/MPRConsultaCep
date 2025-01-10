import requests
import pyodbc
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QDialog, QMessageBox
    
class ResultWindow(QDialog):
    def __init__(self, results):
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
    order = main_window.order_input.text()
    order = order.zfill(8)
    
    # Connect to your SQL Server database
    conn = pyodbc.connect("Driver={SQL Server};Server=tcp:mprsqlserver.database.windows.net,1433;Database=mprDB02;Uid=azureuser;Pwd=GMNh*DfrdzmFkAZD*UfQq9uix;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
    
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    
    # Execute the SQL query to retrieve the transport information based on the order
    cursor.execute("SELECT DestCep FROM PedidosDisponiveis WHERE NumeroDoPedido = ?", order)
    results = cursor.fetchall()
    
    # Close the database connection
    conn.close()
    
    # If the result is found, display it
    if results:
        self.result_window = ResultWindow(results) # Create dialog
        self.result_window.exec() # Show dialog
    else:
        QMessageBox.information(self, "Information", "Order not found.") # Use message box for simple info
    
    return results


























# import requests
# import pyodbc
# from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QDialog, QMessageBox


# def search_order(order, main_window):
#     order = main_window.order_input.text()
#     order = order.zfill(20)  # Keep this if needed

#     conn = pyodbc.connect("Driver={SQL Server};Server=tcp:mprsqlserver.database.windows.net,1433;Database=mprDB02;Uid=azureuser;Pwd=GMNh*DfrdzmFkAZD*UfQq9uix;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")

#     cursor = conn.cursor()

#     # Use a parameterized query
#     cursor.execute("SELECT DestCep FROM PedidosDisponiveis WHERE NumeroDoPedido = ?", order)  # Parameterized query
#     result = cursor.fetchone()

#     if result:
#         print(result)  # Or handle the result as needed
#         QMessageBox.information(main_window, "Order Found", f"CEP: {result[0]}")
#     else:
#         QMessageBox.information(main_window, "Information", "Order not found.")

#     conn.close()  # Important to close the connection
#     return result
