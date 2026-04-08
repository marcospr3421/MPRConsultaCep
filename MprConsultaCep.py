import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QWidget, QDialog,
                             QGridLayout, QMessageBox, QStatusBar, QTabWidget)
from PyQt6.QtGui import QIcon, QFont, QIntValidator
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from SearchCepFunction import search_cep, search_cep_db_logic, ResultWindow as CepResultWindow
from SearchOrderFunction import search_order, search_order_db_logic, ResultWindow as OrderResultWindow
from testeCep import consultar_cep
import requests
import os  # For environment variables
import json
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure Key Vault configuration
KEY_VAULT_NAME = "mprkv2024az"  # Replace with your key vault name
KV_URI = f"https://{KEY_VAULT_NAME}.vault.azure.net"

def get_correios_auth_token():
    """
    Retrieves the base authentication token from Azure Key Vault.

    Returns:
        str: The authentication token if found, otherwise None.
    """
    try:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KV_URI, credential=credential)
        return client.get_secret("CorreiosAuthToken").value
    except Exception as e:
        print(f"Error retrieving secret from Key Vault: {e}")
        return None

def refresh_correios_token():
    """
    Refreshes the Correios API token.

    Fetches a new token from the Correios API and stores it as an
    environment variable.

    Returns:
        str: The new token if successful, otherwise None.
    """
    url = "https://api.correios.com.br/token/v1/autentica/contrato"
    auth_token = get_correios_auth_token()
    
    if not auth_token:
        print("Failed to retrieve authentication token from Key Vault")
        return None
        
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': auth_token
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


from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer

class DatabaseWorker(QObject):
    """
    Background worker for database queries.
    Reliably decouples database operations from the UI thread.
    """
    finished = pyqtSignal(object, object) # results, error

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        print(f"DEBUG WORKER: Thread started for {self.func.__name__}")
        try:
            # We don't have direct access to the cursor here, 
            # so the timeout should be set inside the logic functions.
            results, error = self.func(*self.args)
            print(f"DEBUG WORKER: Finished. Results: {len(results) if results else 0}, Error: {error}")
            self.finished.emit(results, error)
        except Exception as e:
            print(f"DEBUG WORKER: CRASHED: {e}")
            self.finished.emit(None, f"Worker Crash: {str(e)}")


class ResultWindow(QDialog):
    """A dialog window to display formatted query results."""
    def __init__(self, result_text):
        """
        Initializes the ResultWindow.

        Args:
            result_text (str): The text to be displayed, with items
                               potentially separated by newlines or commas.
        """
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
                    result_label.setStyleSheet("background-color: black; font-family: monospace; font-size: 20px; color: white;")
                    result_label.setTextFormat(Qt.TextFormat.PlainText)
                    result_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                    layout.addWidget(result_label)
            else:
                result_label = QLabel(line)
                result_label.setStyleSheet("background-color: black; font-family: monospace; font-size: 20px; color: white;")
                result_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                layout.addWidget(result_label)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    """The main window of the Transport Finder application."""
    def __init__(self):
        """Initializes the main window and sets up the user interface."""
        super().__init__()
        self.setWindowTitle("MPRLabs - Transport Finder - v2.1.12.25")
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





        # Order Search Section
        order_label = QLabel("<b>Procurar dados do Pedido</b>")
        order_label.setObjectName("SectionLabel")
        layout.addWidget(order_label, 1, 0, 1, 2)
        self.order_input = QLineEdit()
        layout.addWidget(self.order_input, 2, 0, 1, 2)
        self.search_button_order = QPushButton("Procurar Pedido")
        self.search_button_order.clicked.connect(self.search_order_func) # Connect directly to the new function
        layout.addWidget(self.search_button_order, 3, 0, 1, 2)
        self.result_label_order = QLabel()
        layout.addWidget(self.result_label_order, 4, 0, 1, 2)
        
        
        # CEP Correios Search Section
        cepCorreios_label = QLabel("<b>Procurar CEP Correios API</b>")
        cepCorreios_label.setObjectName("SectionLabel")
        layout.addWidget(cepCorreios_label, 5, 0, 1, 2)
        self.cepCorreios_input = QLineEdit()
        self.cepCorreios_input.setMaxLength(8)
        self.cepCorreios_input.setValidator(QIntValidator())
        layout.addWidget(self.cepCorreios_input, 6, 0, 1, 2)
        self.search_button_cepCorreios_input = QPushButton("Procurar Correios")
        self.search_button_cepCorreios_input.clicked.connect(self.consultar_cep_func) # Call the correctly named function
        layout.addWidget(self.search_button_cepCorreios_input, 7, 0, 1, 2)
        self.result_label_cepCorreios_input = QLabel()
        layout.addWidget(self.result_label_cepCorreios_input, 8, 0, 1, 2)

        # CEP Search Section
        cep_label = QLabel("Procurar Transportadora por CEP")
        cep_label.setObjectName("SectionLabel")
        layout.addWidget(cep_label, 9, 0, 1, 2)
        self.cep_input = QLineEdit()
        self.cep_input.setMaxLength(8)
        self.cep_input.setValidator(QIntValidator())
        layout.addWidget(self.cep_input, 10, 0, 1, 2)
        self.search_button_cep = QPushButton("Procurar CEP")
        self.search_button_cep.clicked.connect(self.search_cep_func) # Connect directly to the new function
        layout.addWidget(self.search_button_cep, 11, 0, 1, 2)
        self.result_label_cep = QLabel()
        layout.addWidget(self.result_label_cep, 12, 0, 1, 2)

        self.cep_input.setFocus()

    def search_cep_func(self):
        """
        Handles the click event for the 'Procurar por CEP' button using multi-threading.
        """
        cep = self.cep_input.text()
        if not cep:
            QMessageBox.warning(self, "Error", "CEP field cannot be empty.")
            return

        self.status_bar.showMessage("Procurando CEP no banco de dados...")
        self.search_button_cep.setEnabled(False)
        QApplication.processEvents() # Force UI to show "Searching..."

        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self._start_cep_thread(cep))

    def _start_cep_thread(self, cep):
        print(f"DEBUG UI: Preparing CEP thread for {cep}")
        self.thread_cep = QThread()
        self.worker_cep = DatabaseWorker(search_cep_db_logic, cep)
        self.worker_cep.moveToThread(self.thread_cep)
        
        self.thread_cep.started.connect(self.worker_cep.run)
        self.worker_cep.finished.connect(self.on_cep_search_finished)
        self.worker_cep.finished.connect(self.thread_cep.quit)
        self.worker_cep.finished.connect(self.worker_cep.deleteLater)
        self.thread_cep.finished.connect(self.thread_cep.deleteLater)
        
        self.thread_cep.start()

    def on_cep_search_finished(self, results, error):
        print(f"DEBUG UI: CEP search result received.")
        self.status_bar.clearMessage()
        self.search_button_cep.setEnabled(True)

        if error:
            QMessageBox.critical(self, "Database Error", f"A database error occurred:\n\n{error}")
            return

        if results:
            self.result_window = CepResultWindow(results)
            self.result_window.exec()
        else:
            QMessageBox.information(self, "Information", "CEP not found.")

    def search_order_func(self):
        """
        Handles the click event for the 'Procurar por Pedido' button using multi-threading.
        """
        order = self.order_input.text()
        if not order:
            QMessageBox.warning(self, "Error", "ORDER field cannot be empty.")
            return

        self.status_bar.showMessage("Procurando Pedido no banco de dados...")
        self.search_button_order.setEnabled(False)
        QApplication.processEvents() # Force UI to show "Searching..."

        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self._start_order_thread(order))

    def _start_order_thread(self, order):
        print(f"DEBUG UI: Preparing Order thread for {order}")
        self.thread_order = QThread()
        self.worker_order = DatabaseWorker(search_order_db_logic, order)
        self.worker_order.moveToThread(self.thread_order)
        
        self.thread_order.started.connect(self.worker_order.run)
        self.worker_order.finished.connect(self.on_order_search_finished)
        self.worker_order.finished.connect(self.thread_order.quit)
        self.worker_order.finished.connect(self.worker_order.deleteLater)
        self.thread_order.finished.connect(self.thread_order.deleteLater)
        
        self.thread_order.start()

    def on_order_search_finished(self, results, error):
        print(f"DEBUG UI: Order search result received. Results: {len(results) if results else 0}")
        self.status_bar.clearMessage()
        self.search_button_order.setEnabled(True)

        if error:
            QMessageBox.critical(self, "Database Error", f"A database error occurred:\n\n{error}")
            return

        if results:
            self.result_window = OrderResultWindow(results)
            self.result_window.exec()
        else:
            QMessageBox.information(self, "Information", "Order not found.")

    def consultar_cep_func(self):
        """
        Handles the click event for the 'Procurar Correios' button using multi-threading.
        """
        cep_correios = self.cepCorreios_input.text()
        if not cep_correios:
            self.show_message("CEP field cannot be empty", "Please enter a CEP.")
            return

        self.status_bar.showMessage("Consultando API dos Correios...")
        self.search_button_cepCorreios_input.setEnabled(False)

        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self._start_correios_thread(cep_correios))

    def _start_correios_thread(self, cep):
        print(f"DEBUG UI: Preparing Correios thread for {cep}")
        self.thread_correios = QThread()
        self.worker_correios = DatabaseWorker(self._correios_logic, cep)
        self.worker_correios.moveToThread(self.thread_correios)
        
        self.thread_correios.started.connect(self.worker_correios.run)
        self.worker_correios.finished.connect(self.on_correios_finished)
        self.worker_correios.finished.connect(self.thread_correios.quit)
        self.worker_correios.finished.connect(self.worker_correios.deleteLater)
        self.thread_correios.finished.connect(self.thread_correios.deleteLater)
        
        self.thread_correios.start()

    def _correios_logic(self, cep):
        """Helper to run both refresh and search in background."""
        token = refresh_correios_token()
        if not token:
            return None, "Cloud not refresh Correios token."
        
        dados = consultar_cep(cep, token)
        if not dados:
            return None, "CEP not found or API error."
        return dados, None

    def on_correios_finished(self, results, error):
        self.status_bar.clearMessage()
        self.search_button_cepCorreios_input.setEnabled(True)

        if error:
            self.show_message("Error", error)
            return

        if results:
            self.display_result(results, self.result_label_cepCorreios_input)
        else:
            self.show_message("CEP Not Found", "No data returned.")

    def display_result(self, result_text, label):
        """
        Displays results in a new ResultWindow.

        Args:
            result_text (str or dict): The result to display. If it's a
                                       dictionary, it will be converted to a string.
            label (QLabel): The label widget where results might have been
                            previously displayed (not currently used).
        """
        if result_text:
            # Convert the dictionary to a string for ResultWindow
            string_result = str(result_text)
            self.result_window = ResultWindow(string_result) # Pass string_result 
            self.result_window.exec()

    def show_message(self, title, text, informative_text=None):
        """
        Displays a custom-styled message box.

        Args:
            title (str): The title of the message box.
            text (str): The main message text.
            informative_text (str, optional): Additional informative text.
                                              Defaults to None.
        """
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

