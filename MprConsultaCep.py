import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon
from SearchCepFunction import search_cep
from SearchOrderFunction import search_order
from PyQt6.QtGui import QFont, QIcon
from PyQt6 import QtGui
from PyQt6 import QtCore
from testeCep import consultar_cep

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MPRLabs - Transport Finder - v1.0.1.24")
        self.setWindowIcon(QIcon("22994_boat_icon.ico"))
        self.setGeometry(150, 150, 450, 200)
        self.setFixedSize(510, 450)
        self.setStyleSheet("QMainWindow {background-image: url('mprLabs4sml.jpg'); background-repeat: no-repeat; background-position: center;}")
        
        # Create the main widget and layout
        widget = QWidget()
        layout = QVBoxLayout()
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        font2 = QFont()
        font2.setFamily("Arial")
        font2.setPointSize(9)
        
        # Set the layout for the main widget
        widget.setLayout(layout)
        
        # Set the main widget for the main window
        self.setCentralWidget(widget)

        # Create the input field and search button
        self.cep_input = QLineEdit()
        self.cep_input.setStyleSheet("background-color: #FFFF66")
        self.cep_input.setMaxLength(8)
        self.cep_input.setValidator(QtGui.QIntValidator())
        self.search_button_cep = QPushButton("Procurar por CEP")
        self.search_button_cep.setStyleSheet("background-color: lightgreen")
        self.cep_input.returnPressed.connect(self.search_button_cep.click)
        self.search_button_cep.clicked.connect(lambda: search_cep(self, self))
        
        
        # Create the input field and search button
        self.order_input = QLineEdit()
        self.order_input.setStyleSheet("background-color: #FFFF66")
        self.order_input.setMaxLength(20)
        self.search_button_order = QPushButton("Procurar por Pedido")
        self.search_button_order.setStyleSheet("background-color: lightgreen")
        self.order_input.returnPressed.connect(self.search_button_order.click)
        self.search_button_order.clicked.connect(lambda: search_order(self, self))


        # Create the result label
        self.result_label_cep = QLabel()
        self.result_label_cep.setStyleSheet("background-color: white")
        self.result_label_order = QLabel()
        self.result_label_order.setStyleSheet("background-color: white")
        
        # Add the widgets to the layout
        cep_label = QLabel(self)
        cep_label.setText("PROCURE POR CEP")
        cep_label.setStyleSheet("font-family: Arial; font-size: 12pt; font-weight: bold; color: #FE9900; background-color: rgba(71, 71, 71, 0.95)")
        layout.addWidget(cep_label)
        layout.addWidget(self.cep_input)
        layout.addWidget(self.search_button_cep)
        layout.addWidget(self.result_label_cep)
        layout.addStretch()
        
        # Define the order_label variable
        order_label = QLabel("PROCURE POR PEDIDO")
        order_label.setStyleSheet("font-family: Arial; font-size: 12pt; font-weight: bold; color: #FE9900; background-color: rgba(71, 71, 71, 0.95)")
        layout.addWidget(order_label)
        layout.addWidget(self.order_input)        
        self.search_button_correios = QPushButton("Procurar CEP Correios")
        self.search_button_correios.setStyleSheet("background-color: lightblue")
        self.cep_input_correios = QLineEdit()
        self.cep_input_correios.setStyleSheet("background-color: #FFFF66")
        self.cep_input_correios.setMaxLength(8)
        self.cep_input_correios.setValidator(QtGui.QIntValidator())
        self.cep_input_correios.returnPressed.connect(self.search_button_correios.click)
        self.search_button_correios.clicked.connect(self.search_correios)
        layout.addWidget(self.cep_input_correios)
        layout.addWidget(self.search_button_correios)
        self.result_label_correios = QLabel()
        self.result_label_correios.setStyleSheet("background-color: white")
        layout.addWidget(self.result_label_correios)

    def search_correios(self):
        cep = self.cep_input_correios.text()
        token = "eyJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MzYzNjExODIsImlzcyI6InRva2VuLXNlcnZpY2UiLCJleHAiOjE3MzY0NDc1ODIsImp0aSI6IjhmNjVlNjEyLWIwYmEtNGI3Zi1iMWJlLTAxMTVlMDI0N2IyNCIsImFtYmllbnRlIjoiUFJPRFVDQU8iLCJwZmwiOiJQSiIsImlwIjoiNDUuMjI3LjYxLjI0NiwgMTkyLjE2OC4xLjEzMCIsImNhdCI6IlBsMCIsImNvbnRyYXRvIjp7Im51bWVybyI6Ijk5MTIzNzM3MzQiLCJkciI6NzIsImFwaXMiOlt7ImFwaSI6Mjd9LHsiYXBpIjozNH0seyJhcGkiOjM1fSx7ImFwaSI6NDF9LHsiYXBpIjo3Nn0seyJhcGkiOjc4fSx7ImFwaSI6ODd9LHsiYXBpIjo1NjZ9LHsiYXBpIjo1ODZ9LHsiYXBpIjo1ODd9LHsiYXBpIjo2MjF9LHsiYXBpIjo2MjN9XX0sImlkIjoiYXpjb21lcmNpbyIsImNucGoiOiIyMDM4NDg0OTAwMDExMyJ9.l8zENOSVUqIBfPquRPQjBRhPLilnHCDklJtGHxU2e1obHpSsZ9au_AMTdv7sWksdcOE_IaCTmfm0pmjPK01G9atRrf7GBq1Eh1Z2d-YmPkyFnEYbV1zF3pLgACYYmCdFxuvXR0uhCteWIeTz5Wn1-DIVT2CkpgKxGr2uq3QzBnuGUtmQZeXW0wdHZ6ebmRu9GeagG4lm-i3fTvweyBQnWGFCCZj9wlwKNTmfwyv-zApCenWGqVUZDXaPIgqc6CP6lb7oLCuwXSKYrRzKI4qYg9cBYkTCc60oWfJvRR0ci4OB-LNZu-vpdjGGf7cs5hauVUQ0eeJGFwV3kqgGTQeHWw'"
        dados_cep = consultar_cep(cep, token)
        if dados_cep != None:
            print("\nInformações do CEP:")
            for chave, valor in dados_cep.items():
                print(f"{chave}: {valor}")
                self.result_label_correios.setText(str(dados_cep))
        else:
            self.result_label_correios.setText("CEP não encontrado")
            

        
        
        
        
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
