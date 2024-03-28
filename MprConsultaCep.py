import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
import requests
import pyodbc

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CEP Search")
        
        # Create the main widget and layout
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Create the input field and search button
        self.cep_input = QLineEdit()
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_cep)
        
        # Create the result label
        self.result_label = QLabel()
        
        # Add the widgets to the layout
        layout.addWidget(QLabel("Enter the CEP:"))
        layout.addWidget(self.cep_input)
        layout.addWidget(self.search_button)
        layout.addWidget(self.result_label)
        
        # Set the layout for the main widget
        widget.setLayout(layout)
        
        # Set the main widget for the main window
        self.setCentralWidget(widget)
    
    def search_cep(self):
        cep = self.cep_input.text()
        cep = cep.zfill(8)
        
        # Connect to your SQL Server database
        conn = pyodbc.connect("Driver={SQL Server};Server=tcp:mprsqlserver.database.windows.net,1433;Database=mprDB02;Uid=azureuser;Pwd=Zaqmko21@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
        
        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()
        
        # Execute the SQL query to retrieve the transport information based on the CEP
        cursor.execute(f"SELECT * FROM TransportTable WHERE '{cep}' BETWEEN CepInicial AND CepFinal")
        results = cursor.fetchall()
        
        # Close the database connection
        conn.close()
        
        # If the result is found, display it
        if results:
            self.result_label.setText(str(results))
            result_list = [f"Transport ID: {result[0]}, CEP Inicial: {result[1]}, CEP Final: {result[2]}, Cidade: {result[3]} Estado: {result[4]}, Transportador: {result[5]}" for result in results]
            self.result_label.setText("\n".join(result_list))
        else:
            # If the result is not found, use the Postmon API as a fallback
            url = f"https://api.postmon.com.br/v1/cep/{cep}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self.result_label.setText(str(data))
            else:
                self.result_label.setText("CEP not found.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())