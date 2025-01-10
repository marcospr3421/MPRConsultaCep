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
                line = f"CIDADE: {result[3]} - UF: {result[4]} - TRANSPORTE: {result[5]}"
                result_label = QLabel(line)  # Create label for each result
                layout.addWidget(result_label)
        else:
             layout.addWidget(QLabel("No results found.")) # Clear message if no results

        self.setLayout(layout)

    
def search_cep(self,main_window):
    cep = main_window.cep_input.text()
    cep = cep.zfill(8)
    
    # Connect to your SQL Server database
    conn = pyodbc.connect("Driver={SQL Server};Server=tcp:mprsqlserver.database.windows.net,1433;Database=mprDB02;Uid=azureuser;Pwd=GMNh*DfrdzmFkAZD*UfQq9uix;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
    
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    
    # Execute the SQL query to retrieve the transport information based on the CEP
    cursor.execute(f"SELECT * FROM TransportTable WHERE '{cep}' BETWEEN CepInicial AND CepFinal")
    results = cursor.fetchall()
    
    # Close the database connection
    conn.close()
    
    # If the result is found, display it
    if results:
        self.result_window = ResultWindow(results) # Create dialog
        self.result_window.exec() # Show dialog
    else:
        QMessageBox.information(self, "Information", "CEP not found.") # Use message box for simple info
    
    return results