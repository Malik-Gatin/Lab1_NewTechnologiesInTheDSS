from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton

class DataInputDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Введите данные")
        layout = QVBoxLayout()

        self.class_label_input = QLineEdit()
        self.class_label_input.setPlaceholderText("Метка класса")
        layout.addWidget(self.class_label_input)

        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Ширина")
        layout.addWidget(self.width_input)

        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Высота")
        layout.addWidget(self.height_input)

        self.submit_button = QPushButton("OK")
        self.submit_button.clicked.connect(self.on_submit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

        self.class_label = None
        self.width = None
        self.height = None

    def on_submit(self):
        self.class_label = self.class_label_input.text()
        self.width = self.width_input.text()
        self.height = self.height_input.text()
        self.accept()