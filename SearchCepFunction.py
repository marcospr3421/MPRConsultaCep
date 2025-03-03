import pyodbc
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QDialog, QMessageBox, QGridLayout
    
class ResultWindow(QDialog):
    def __init__(self, results):
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
    cep = main_window.cep_input.text()
    cep = cep.zfill(8)
    
    # Connect to your SQL Server database
    conn = pyodbc.connect("Driver={SQL Server};Server=tcp:mprsqlserver.database.windows.net,1433;Database=mprDB02;Uid=azureuser;Pwd=GMNh*DfrdzmFkAZD*UfQq9uix;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
    
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    
    # Execute the SQL query to retrieve the transport information based on the CEP
    cursor.execute(f"SELECT * FROM TransportTable WHERE '{cep}' BETWEEN CepInicial AND CepFinal order by Transportador ASC")
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
