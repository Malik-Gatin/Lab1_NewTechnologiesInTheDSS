from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QSpinBox, QPushButton
from core.download_images import *

class ImageDownloadDialog(QDialog):
    def __init__(self, parent=None):
        super(ImageDownloadDialog, self).__init__(parent)

        self.setWindowTitle("Загрузка изображений")
        layout = QVBoxLayout()

        self.class_name_label = QLabel("Название класса:")
        self.class_name_input = QLineEdit()
        layout.addWidget(self.class_name_label)
        layout.addWidget(self.class_name_input)

        self.full_size_checkbox = QCheckBox("Полный размер?")
        layout.addWidget(self.full_size_checkbox)

        self.image_count_label = QLabel("Количество изображений:")
        self.image_count_input = QSpinBox()
        self.image_count_input.setMinimum(1)
        layout.addWidget(self.image_count_label)
        layout.addWidget(self.image_count_input)

        self.download_button = QPushButton("Загрузить")
        self.download_button.clicked.connect(self.download_images1)
        layout.addWidget(self.download_button)

        self.setLayout(layout)

    def open_download_dialog(self):
        download_dialog = ImageDownloadDialog(self)
        download_dialog.exec_()

    def download_images1(self):
        class_name = self.class_name_input.text()
        is_full_size = self.full_size_checkbox.isChecked()
        image_count = self.image_count_input.value()
        download_images(class_name, image_count, is_full_size)

        print("Загрузка...")
        print(f"Название класса: {class_name}")
        print(f"Полный размер: {is_full_size}")
        print(f"Количество изображений: {image_count}")
        self.close()