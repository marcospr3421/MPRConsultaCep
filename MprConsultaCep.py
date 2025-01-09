import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QWidget, QDialog,
                             QGridLayout, QMessageBox, QStatusBar)
from PyQt6.QtGui import QIcon, QFont, QIntValidator
from PyQt6.QtCore import Qt
from SearchCepFunction import search_cep
from SearchOrderFunction import search_order
from testeCep import consultar_cep

class ResultWindow(QDialog):
    def __init__(self, result_text):
        super().__init__()
        self.setWindowTitle("Resultado da Consulta")
        layout = QVBoxLayout()
        result_label = QLabel(result_text)
        result_label.setStyleSheet("background-color: white; font-family: monospace;")  # Use monospace font
        result_label.setTextFormat(Qt.TextFormat.PlainText)  # Ensure plain text display
        layout.addWidget(result_label)
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
        self.order_input.setMaxLength(8)
        self.order_input.setValidator(QIntValidator())
        layout.addWidget(self.order_input, 2, 0, 1, 2)  # Span 2 columns
        self.search_button_order = QPushButton("Search Order")
        self.search_button_order.clicked.connect(self.search_order_func) # Connect directly to the new function
        layout.addWidget(self.search_button_order, 3, 0, 1, 2)  # Span 2 columns
        self.result_label_order = QLabel()
        # self.result_label_order.setStyleSheet("background-color: #444; border: 1px solid #666;")  #Restyled for consistency
        # layout.addWidget(self.result_label_order, 4, 0, 1, 2)  # Span 2 columns, next row
        
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
        # self.result_label_cepCorreios_input.setStyleSheet("background-color: #444; border: 1px solid #666;")  #Restyled for consistency
        # layout.addWidget(self.result_label_cepCorreios_input, 8, 0, 1, 2)  # Span 2 columns
        
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
        self.result_label_cep.setStyleSheet("background-color: #444; border: 1px solid #666;")  #Restyled for consistency
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
        if not order:  # Check if ORDER is empty
            QMessageBox.warning(self, "Error", "ORDER field cannot be empty.")
            return
        search_order(self, self)
        
    def consultar_cep_func(self):  # Rename for clarity (was just consultar_cep)
        cep_correios = self.cepCorreios_input.text() # Get the TEXT of the input

        if not cep_correios:
            QMessageBox.warning(self, "Error", "API Correios field cannot be empty.")
            return
        
        # Pass the CEP string, NOT 'self'.  Remove unnecessary second argument.
        dados_cep = consultar_cep(cep_correios, "eyJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MzYzNjExODIsImlzcyI6InRva2VuLXNlcnZpY2UiLCJleHAiOjE3MzY0NDc1ODIsImp0aSI6IjhmNjVlNjEyLWIwYmEtNGI3Zi1iMWJlLTAxMTVlMDI0N2IyNCIsImFtYmllbnRlIjoiUFJPRFVDQU8iLCJwZmwiOiJQSiIsImlwIjoiNDUuMjI3LjYxLjI0NiwgMTkyLjE2OC4xLjEzMCIsImNhdCI6IlBsMCIsImNvbnRyYXRvIjp7Im51bWVybyI6Ijk5MTIzNzM3MzQiLCJkciI6NzIsImFwaXMiOlt7ImFwaSI6Mjd9LHsiYXBpIjozNH0seyJhcGkiOjM1fSx7ImFwaSI6NDF9LHsiYXBpIjo3Nn0seyJhcGkiOjc4fSx7ImFwaSI6ODd9LHsiYXBpIjo1NjZ9LHsiYXBpIjo1ODZ9LHsiYXBpIjo1ODd9LHsiYXBpIjo2MjF9LHsiYXBpIjo2MjN9XX0sImlkIjoiYXpjb21lcmNpbyIsImNucGoiOiIyMDM4NDg0OTAwMDExMyJ9.l8zENOSVUqIBfPquRPQjBRhPLilnHCDklJtGHxU2e1obHpSsZ9au_AMTdv7sWksdcOE_IaCTmfm0pmjPK01G9atRrf7GBq1Eh1Z2d-YmPkyFnEYbV1zF3pLgACYYmCdFxuvXR0uhCteWIeTz5Wn1-DIVT2CkpgKxGr2uq3QzBnuGUtmQZeXW0wdHZ6ebmRu9GeagG4lm-i3fTvweyBQnWGFCCZj9wlwKNTmfwyv-zApCenWGqVUZDXaPIgqc6CP6lb7oLCuwXSKYrRzKI4qYg9cBYkTCc60oWfJvRR0ci4OB-LNZu-vpdjGGf7cs5hauVUQ0eeJGFwV3kqgGTQeHWw'")  # Replace with your actual token

        if dados_cep:
            self.display_result(str(dados_cep), self.result_label_cepCorreios_input)
        else:
            QMessageBox.warning(self, "Error", "CEP not found or API error.")


        
    def display_result(self, result_text, label): #Generalized function for displaying results
        if isinstance(result_text, list): #handles list results from database queries
            result_text = "\n".join([str(item) for item in result_text] ) #Format nicely


        if result_text:
            self.result_window = ResultWindow(result_text)
            self.result_window.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
        
        
        
        
        
#         self.search_button_correios = QPushButton("Procurar CEP Correios")  # Create button
#         self.search_button_correios.setStyleSheet("background-color: lightblue")
#         self.cep_input_correios = QLineEdit()  # Create the LineEdit
#         self.cep_input_correios.setStyleSheet("background-color: #FFFF66")
#         self.cep_input_correios.setMaxLength(8)
#         self.cep_input_correios.setValidator(QtGui.QIntValidator())
#         self.cep_input_correios.returnPressed.connect(self.search_button_correios.click)
#         self.search_button_correios.clicked.connect(self.search_correios)
#         self.result_label_correios = QLabel()
#         self.result_label_correios.setStyleSheet("background-color: white")
        
#         # Create the main widget and layout
#         widget = QWidget()
#         layout = QVBoxLayout()
#         font = QFont()
#         font.setFamily("Arial")
#         font.setPointSize(14)
#         font2 = QFont()
#         font2.setFamily("Arial")
#         font2.setPointSize(9)
        
#         # Set the layout for the main widget
#         widget.setLayout(layout)
        
#         # Set the main widget for the main window
#         self.setCentralWidget(widget)

#         # Create the input field and search button
#         self.cep_input = QLineEdit()
#         self.cep_input.setStyleSheet("background-color: #FFFF66")
#         self.cep_input.setMaxLength(8)
#         self.cep_input.setValidator(QtGui.QIntValidator())
#         self.search_button_cep = QPushButton("Procurar por CEP")
#         self.search_button_cep.setStyleSheet("background-color: lightgreen")
#         self.cep_input.returnPressed.connect(self.search_button_cep.click)
#         self.search_button_cep.clicked.connect(lambda: search_cep(self, self))
        
        
#         # Create the input field and search button
#         self.order_input = QLineEdit()
#         self.order_input.setStyleSheet("background-color: #FFFF66")
#         self.order_input.setMaxLength(20)
#         self.search_button_order = QPushButton("Procurar por Pedido")
#         self.search_button_order.setStyleSheet("background-color: lightgreen")
#         self.order_input.returnPressed.connect(self.search_button_order.click)
#         self.search_button_order.clicked.connect(lambda: search_order(self, self))


#         # Create the result label
#         self.result_label_cep = QLabel()
#         self.result_label_cep.setStyleSheet("background-color: white")
#         self.result_label_order = QLabel()
#         self.result_label_order.setStyleSheet("background-color: white")
        
#         # Add the widgets to the layout
#         cep_label = QLabel(self)
#         cep_label.setText("PROCURE POR CEP")
#         cep_label.setStyleSheet("font-family: Arial; font-size: 12pt; font-weight: bold; color: #FE9900; background-color: rgba(71, 71, 71, 0.95)")
#         layout.addWidget(cep_label)
#         layout.addWidget(self.cep_input)
#         layout.addWidget(self.search_button_cep)
#         layout.addWidget(self.result_label_cep)
#         layout.addStretch()
        
#         # Define the order_label variable
#         order_label = QLabel("PROCURE POR PEDIDO")
#         order_label.setStyleSheet("font-family: Arial; font-size: 12pt; font-weight: bold; color: #FE9900; background-color: rgba(71, 71, 71, 0.95)")
#         layout.addWidget(order_label)
#         layout.addWidget(self.order_input)
#         layout.addWidget(self.search_button_order)
#         layout.addWidget(self.result_label_order)
#         layout.addStretch()
        
        
#         correios_label = QLabel("PROCURE POR CEP CORREIOS")
#         correios_label.setStyleSheet("font-family: Arial; font-size: 12pt; font-weight: bold; color: #FE9900; background-color: rgba(71, 71, 71, 0.95)")
#         layout.addWidget(correios_label)   
#         layout.addWidget(self.cep_input_correios)  # Now this will work!
#         layout.addWidget(self.search_button_correios)
#         layout.addWidget(self.result_label_correios)
#         layout.addStretch()

        

        

#     def search_correios(self):
#         cep = self.cep_input_correios.text()
#         token = "eyJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MzYzNjExODIsImlzcyI6InRva2VuLXNlcnZpY2UiLCJleHAiOjE3MzY0NDc1ODIsImp0aSI6IjhmNjVlNjEyLWIwYmEtNGI3Zi1iMWJlLTAxMTVlMDI0N2IyNCIsImFtYmllbnRlIjoiUFJPRFVDQU8iLCJwZmwiOiJQSiIsImlwIjoiNDUuMjI3LjYxLjI0NiwgMTkyLjE2OC4xLjEzMCIsImNhdCI6IlBsMCIsImNvbnRyYXRvIjp7Im51bWVybyI6Ijk5MTIzNzM3MzQiLCJkciI6NzIsImFwaXMiOlt7ImFwaSI6Mjd9LHsiYXBpIjozNH0seyJhcGkiOjM1fSx7ImFwaSI6NDF9LHsiYXBpIjo3Nn0seyJhcGkiOjc4fSx7ImFwaSI6ODd9LHsiYXBpIjo1NjZ9LHsiYXBpIjo1ODZ9LHsiYXBpIjo1ODd9LHsiYXBpIjo2MjF9LHsiYXBpIjo2MjN9XX0sImlkIjoiYXpjb21lcmNpbyIsImNucGoiOiIyMDM4NDg0OTAwMDExMyJ9.l8zENOSVUqIBfPquRPQjBRhPLilnHCDklJtGHxU2e1obHpSsZ9au_AMTdv7sWksdcOE_IaCTmfm0pmjPK01G9atRrf7GBq1Eh1Z2d-YmPkyFnEYbV1zF3pLgACYYmCdFxuvXR0uhCteWIeTz5Wn1-DIVT2CkpgKxGr2uq3QzBnuGUtmQZeXW0wdHZ6ebmRu9GeagG4lm-i3fTvweyBQnWGFCCZj9wlwKNTmfwyv-zApCenWGqVUZDXaPIgqc6CP6lb7oLCuwXSKYrRzKI4qYg9cBYkTCc60oWfJvRR0ci4OB-LNZu-vpdjGGf7cs5hauVUQ0eeJGFwV3kqgGTQeHWw'"
#         dados_cep = consultar_cep(cep, token)
#         if dados_cep:
#             result_text = ""
#             for chave, valor in dados_cep.items():
#                 result_text += f"{chave}: {valor}\n"

#             self.result_window = ResultWindow(result_text)  # Create an instance
#             self.result_window.exec()  # Show the dialog modally


#         else:
#             self.result_window = ResultWindow("CEP não encontrado")  # For errors
#             self.result_window.exec()


            

        
        
        
        
    


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec())
