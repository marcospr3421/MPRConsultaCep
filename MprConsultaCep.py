import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon
from SearchCepFunction import search_cep
from SearchOrderFunction import search_order
from PyQt6.QtGui import QFont, QIcon
from PyQt6 import QtGui

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
        layout.addWidget(self.search_button_order)
        layout.addWidget(self.result_label_order)
        layout.addStretch()
        
        # Set the layout for the main widget
        widget.setLayout(layout)
        
        # Set the main widget for the main window
        self.setCentralWidget(widget)
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())