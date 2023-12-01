from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap
from iterator import Iterator

class ImageDisplayDialog(QDialog):
    def __init__(self, df, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Изображение")
        layout = QVBoxLayout()

        self.iterator = iter(Iterator(df))

        self.image_label = QLabel()
        self.name_label = QLabel()
        layout.addWidget(self.image_label)
        layout.addWidget(self.name_label)

        self.next_button = QPushButton("Далее")
        self.next_button.clicked.connect(self.show_next_image)
        self.show_next_image()
        layout.addWidget(self.next_button)

        self.setLayout(layout)

    def show_next_image(self):
        try:
            image_path = next(self.iterator)
            pixmap = QPixmap(image_path[3])
            self.image_label.setPixmap(pixmap.scaledToWidth(500))
            self.name_label.setText(image_path[3])
        except:
            StopIteration
        pass