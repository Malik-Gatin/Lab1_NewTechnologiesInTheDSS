from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog

class TextDisplayWindow(QDialog):
    def __init__(self, text:str):
        super().__init__()
        self.setWindowTitle('Сообщение')
        self.adjustSize()

        self.text_label = QLabel()
        self.text_label.setText(text)

        layout = QVBoxLayout()
        layout.addWidget(self.text_label)

        self.setLayout(layout)