import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from SearchCepFunction import search_cep

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
        self.search_button.clicked.connect(search_cep)
        
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
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())