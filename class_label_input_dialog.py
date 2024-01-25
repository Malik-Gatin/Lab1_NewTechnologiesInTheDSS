from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout

class ClassLabelInputDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Введите метку класса")

        layout = QVBoxLayout()

        label = QLabel("Введите метку класса:")
        self.class_label_input = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(self.class_label_input)

        confirm_button = QPushButton("OK")
        confirm_button.clicked.connect(self.confirm_label)
        layout.addWidget(confirm_button)

        self.setLayout(layout)

        self.result_label = None

    def confirm_label(self):
        self.result_label = self.class_label_input.text()
        self.accept()