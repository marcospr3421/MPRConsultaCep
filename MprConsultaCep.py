import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon
from SearchCepFunction import search_cep

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MPRLabs - Consulta CEP - v1.0.0.24")
        self.setWindowIcon(QIcon("22994_boat_icon.ico"))
        
        # Create the main widget and layout
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Create the input field and search button
        self.cep_input = QLineEdit()
        self.search_button = QPushButton("Procurar")
        self.cep_input.returnPressed.connect(self.search_button.click)
        self.search_button.clicked.connect(lambda: search_cep(self, self))
        
        # Create the result label
        self.result_label = QLabel()
        
        # Add the widgets to the layout
        layout.addWidget(QLabel("Digite o CEP:"))
        layout.addWidget(self.cep_input)
        layout.addWidget(self.search_button)
        layout.addWidget(self.result_label)
        
        # Set the layout for the main widget
        widget.setLayout(layout)
        
        # Set the main widget for the main window
        self.setCentralWidget(widget)
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())