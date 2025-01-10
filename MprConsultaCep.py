import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QWidget, QDialog,
                             QGridLayout, QMessageBox, QStatusBar)
from PyQt6.QtGui import QIcon, QFont, QIntValidator
from PyQt6.QtCore import Qt
from SearchCepFunction import search_cep
from SearchOrderFunction import search_order
from testeCep import consultar_cep
import requests
import os  # For environment variables (example)
import json

def refresh_correios_token():
    url = "https://api.correios.com.br/token/v1/autentica/contrato"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Basic YXpjb21lcmNpbzphQ3hIQjZiczQweGVPS1U4QUx6MVNscVdhZDh1OHBBcFJjVHc5Ymx0' #Stored securely as env var.
    }
    data = {
        "numero": "9912373734",  # Shouldn't change.
        "dr": 72  # Shouldn't change.
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        response_json = response.json() # Get the full JSON response

        new_token = response_json.get('token') # Extract the "token" field

        if new_token is None:
            print(f"Unexpected API response: {response_json}")
            raise ValueError("API did not return a token in the 'token' field.")

        os.environ['CORREIOS_TOKEN'] = new_token  # Store the actual token string
        print("Token refreshed successfully!")
        return new_token  # Return the extracted token



    except requests.exceptions.RequestException as e:
        print(f"Error refreshing token: {e}")  # Still log for troubleshooting
        return None # Explicitly return None to signal failure






class ResultWindow(QDialog):
    def __init__(self, result_text):
        super().__init__()
        self.setWindowTitle("Resultado da Consulta")
        layout = QVBoxLayout()

        # Split the result text into lines
        lines = result_text.split('\n')
        for i, line in enumerate(lines):
            if ',' in line:
                items = line.split(',')
                for item in items:
                    result_label = QLabel(item.strip())
                    result_label.setStyleSheet("background-color: white; font-family: monospace;")
                    result_label.setTextFormat(Qt.TextFormat.PlainText)
                    layout.addWidget(result_label)
            else:
                result_label = QLabel(line)
                result_label.setStyleSheet("background-color: white; font-family: monospace;")
                result_label.setTextFormat(Qt.TextFormat.PlainText)
                layout.addWidget(result_label)


        # Create a label for each line
        for line in lines:
            result_label = QLabel(line)
            result_label.setStyleSheet("background-color: white; font-family: monospace;")
            result_label.setTextFormat(Qt.TextFormat.PlainText)


        self.setLayout(layout)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MPRLabs - Transport Finder - v2.0.1.25")
        self.setWindowIcon(QIcon("22994_boat_icon.ico"))
        self.setGeometry(150, 150, 510, 550)  # Set initial size
        self.setMinimumSize(510, 550)  # Set minimum size

        # Use a more visually appealing style sheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #333;
                color: #eee;
            }
            QPushButton {
                background-color: #555;
                border: 1px solid #777;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QLineEdit {
                background-color: #444;
                border: 1px solid #666;
                padding: 3px;
            }
            QLabel {
                color: #eee;  /* Consistent text color on labels */
                padding: 5px; /* Consistent padding on Labels */

            }

            QLabel#TitleLabel{ /* Styled title label */
                font-size: 16pt;
                font-weight: bold;
                color: #FE9900;
                background-color: transparent;
                padding: 10px;
            }

            QLabel#SectionLabel { /* Section header labels */
                font-size: 12pt;
                font-weight: bold;
                color: #FE9900;
                background-color: transparent;
                padding: 5px;

            }


        """)

        central_widget = QWidget()
        layout = QGridLayout() # Changed layout for organization
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)



        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)


        # Title Label (Improved)
        title_label = QLabel("MPRLabs Transport Finder")
        title_label.setObjectName("TitleLabel")  # For styling
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the title
        layout.addWidget(title_label, 0, 0, 1, 3) # span 3 columns




        # Order Search Section
        order_label = QLabel("Search by ORDER")
        order_label.setObjectName("SectionLabel")
        layout.addWidget(order_label, 1, 0, 1, 2)  # Span 2 columns
        self.order_input = QLineEdit()
        layout.addWidget(self.order_input, 2, 0, 1, 2)  # Span 2 columns
        self.search_button_order = QPushButton("Search Order")
        self.search_button_order.clicked.connect(self.search_order_func) # Connect directly to the new function
        layout.addWidget(self.search_button_order, 3, 0, 1, 2)  # Span 2 columns
        self.result_label_order = QLabel()
        layout.addWidget(self.result_label_order, 4, 0, 1, 2)
        
        
        # CEP Correios Search Section
        cepCorreios_label = QLabel("Search by API Correios")
        cepCorreios_label.setObjectName("SectionLabel")
        layout.addWidget(cepCorreios_label, 5, 0, 1, 2)  # Span 2 columns, start below Order section
        self.cepCorreios_input = QLineEdit()
        self.cepCorreios_input.setMaxLength(8)
        self.cepCorreios_input.setValidator(QIntValidator())
        layout.addWidget(self.cepCorreios_input, 6, 0, 1, 2)  # Span 2 columns
        self.search_button_cepCorreios_input = QPushButton("Search API Correios")
        self.search_button_cepCorreios_input.clicked.connect(self.consultar_cep_func) # Call the correctly named function
        layout.addWidget(self.search_button_cepCorreios_input, 7, 0, 1, 2)  # Span 2 columns
        self.result_label_cepCorreios_input = QLabel()
        layout.addWidget(self.result_label_cepCorreios_input, 8, 0, 1, 2)

        # CEP Search Section
        cep_label = QLabel("Search by CEP")
        cep_label.setObjectName("SectionLabel")
        layout.addWidget(cep_label, 9, 0, 1, 2)
        self.cep_input = QLineEdit()
        self.cep_input.setMaxLength(8)
        self.cep_input.setValidator(QIntValidator())
        layout.addWidget(self.cep_input, 10, 0, 1, 2)
        self.search_button_cep = QPushButton("Search CEP")
        self.search_button_cep.clicked.connect(self.search_cep_func) # Connect directly to the new function
        layout.addWidget(self.search_button_cep, 11, 0, 1, 2)
        self.result_label_cep = QLabel()
        layout.addWidget(self.result_label_cep, 12, 0, 1, 2) # span two columns

        self.cep_input.setFocus()

    def search_cep_func(self):

        cep = self.cep_input.text()
        if not cep:  # Check if CEP is empty
            QMessageBox.warning(self, "Error", "CEP field cannot be empty.")
            return
        search_cep(self, self)



    def search_order_func(self):
        order = self.order_input.text()

        if not order:
            QMessageBox.warning(self, "Error", "ORDER field cannot be empty.")
            return
        search_order(self, self)

        




    def consultar_cep_func(self):
        cep_correios = self.cepCorreios_input.text()
        token = os.environ.get('CORREIOS_TOKEN') #Fetch the token.  Use string key, not list.
        if not token:
            print("Token not available. Refreshing...")
        token = refresh_correios_token()
        if token is None:  # Handle refresh failure
            self.show_message("Token Refresh Failed", "Could not refresh the Correios token.  Check your connection or credentials.")  # Display error message
            return # Stop further processing
        if not cep_correios:
            self.show_message("CEP field cannot be empty", "Please enter a CEP.")
            return

        # Pass the CEP string and token.
        dados_cep = consultar_cep(cep_correios, token)

        if dados_cep:
            self.display_result(str(dados_cep), self.result_label_cepCorreios_input)
        else:
            self.show_message("CEP Não Encontrado", f"CEP digitado: {cep_correios} não foi encontrado ou é inválido.", "Validar o CEP digitado e tentar novamente.")

  

    def display_result(self, result_text, label):
        #  Existing dialog logic
        if isinstance(result_text, list) or isinstance(result_text, tuple):
             result_text = "\n".join([str(item) for item in result_text])       
        
        if result_text:
            self.result_window = ResultWindow(result_text) #corrected function call
            self.result_window.exec()
            
            
            
    def show_message(self, title, text,     informative_text=None): # Add parameters

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)    # Use the title argument
        msg_box.setText(text)          # Use the text argument

        if informative_text:  # Set informative text only if provided
            msg_box.setInformativeText(informative_text)


        font = msg_box.font()
        font.setPointSize(14)
        font.setBold(True)
        msg_box.setFont(font)

        msg_box.setStyleSheet("QLabel { color: red; }")
        msg_box.setIcon(QMessageBox.Icon.Warning)

        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        retval = msg_box.exec()

        # ... process retval if needed
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

