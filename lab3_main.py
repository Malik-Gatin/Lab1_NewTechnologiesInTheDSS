import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QFileDialog, QTableWidget, QTableWidgetItem, QSizePolicy, QDialog, QLabel, QDateEdit
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDateEdit, QDialogButtonBox,QLineEdit, QCheckBox, QSpinBox
import pandas as pd
from datetime import datetime

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
        #download_images(class_name, image_count, is_full_size)

        # Выполнить операцию загрузки с полученной информацией
        # Например: download_images(class_name, is_full_size, image_count)
        print("Загрузка...")
        print(f"Название класса: {class_name}")
        print(f"Полный размер: {is_full_size}")
        print(f"Количество изображений: {image_count}")
        self.close()

class DateInputDialog(QDialog):
    def __init__(self, parent=None):
        super(DateInputDialog, self).__init__(parent)

        self.setWindowTitle("Enter Date")

        layout = QVBoxLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(datetime.now().date())

        layout.addWidget(QLabel("Enter the date:"))
        layout.addWidget(self.date_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_date(self):
        return self.date_edit.date().toString("yyyy-MM-dd")

class ImageDownloadApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Download App")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.start_button = QPushButton("Image Download")
        self.start_button.clicked.connect(self.start_download)
        self.layout.addWidget(self.start_button)

        self.choose_file_button = QPushButton("Choose CSV File")
        self.choose_file_button.clicked.connect(self.choose_csv_file)
        self.layout.addWidget(self.choose_file_button)

        self.dataset_table = QTableWidget()
        self.layout.addWidget(self.dataset_table)

        self.step1_button = QPushButton("Step 1: Split into X and Y CSV files")
        self.step1_button.clicked.connect(self.step1_split_xy)
        self.layout.addWidget(self.step1_button)

        self.step2_button = QPushButton("Step 2: Split into Yearly CSV files")
        self.step2_button.clicked.connect(self.step2_split_yearly)
        self.layout.addWidget(self.step2_button)

        self.step3_button = QPushButton("Step 3: Split into Weekly CSV files")
        self.step3_button.clicked.connect(self.step3_split_weekly)
        self.layout.addWidget(self.step3_button)

        self.step4_button = QPushButton("Step 4: Get Data by Date")
        self.step4_button.clicked.connect(self.open_date_dialog)
        self.layout.addWidget(self.step4_button)

        self.central_widget.setLayout(self.layout)

        self.dataset = None

        # Устанавливаем политику изменения размера для central_widget
        self.central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def open_download_dialog(self):
        download_dialog = ImageDownloadDialog()
        download_dialog.exec_()

    def start_download(self):
        self.image_download_dialog = ImageDownloadDialog(self)
        self.image_download_dialog.open_download_dialog()


    def choose_csv_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            self.load_dataset(file_name)
            print(f"Selected CSV File: {file_name}")

    def load_dataset(self, file_name):
        try:
            self.dataset = pd.read_csv(file_name)

            # Очистим QTableWidget перед добавлением новых данных
            self.dataset_table.clear()
            self.dataset_table.setRowCount(0)
            self.dataset_table.setColumnCount(len(self.dataset.columns))

            # Устанавливаем заголовки столбцов
            self.dataset_table.setHorizontalHeaderLabels(self.dataset.columns)

            # Заполняем таблицу данными
            for row in range(len(self.dataset)):
                self.dataset_table.insertRow(row)
                for col in range(len(self.dataset.columns)):
                    item = QTableWidgetItem(str(self.dataset.iloc[row, col]))
                    self.dataset_table.setItem(row, col, item)

            # Динамически регулируем ширину столбцов
            self.dataset_table.resizeColumnsToContents()

            # Измеряем ширину всех столбцов
            total_width = sum(self.dataset_table.columnWidth(col) for col in range(self.dataset_table.columnCount()))

            # Определяем высоту окна в зависимости от количества записей в таблице
            max_rows = 30
            height = min(len(self.dataset), max_rows) * 25 + 100  # Примерный размер строки: 25 пикселей

            # Устанавливаем ширину и высоту окна
            self.resize(total_width + 100, height)

        except Exception as e:
            print(f"Error loading dataset: {str(e)}")
            self.dataset = None

    def step1_split_xy(self):
        if self.dataset is not None:
            #separate_data_into_date_and_data(df)
            pass
        else:
            print("Please choose a CSV file first.")

    def step2_split_yearly(self):
        if self.dataset is not None:
            # Вызов функции для выполнения шага 2
            pass
        else:
            print("Please choose a CSV file first.")

    def step3_split_weekly(self):
        if self.dataset is not None:
            # Вызов функции для выполнения шага 3
            pass
        else:
            print("Please choose a CSV file first.")

    def open_date_dialog(self):
        date_dialog = DateInputDialog(self)
        result = date_dialog.exec_()
        if result == QDialog.Accepted:
            date_input = date_dialog.get_date()
            self.step4_get_data_by_date(date_input)

    def step4_get_data_by_date(self, date_str):
        if self.dataset is not None:
            try:
                date_to_get = datetime.strptime(date_str, "%Y-%m-%d")
                data = self.get_data_by_date(date_to_get)
                if data is not None:
                    print(data)
                else:
                    print(f"No data available for the date: {date_to_get}")
            except ValueError:
                print("Invalid date format. Please enter the date in the format YYYY-MM-DD.")
        else:
            print("Please choose a CSV file first.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageDownloadApp()
    window.show()
    #download_all_images()
    #csv_file_tiger_full = create_file_path("tiger", True)
    #df = create_data_frame_from_csv(csv_file_tiger_full , IMAGES_FIELDS)
    #print(df)
    #write_another_dates(df, datetime(2023, 1, 1))
    #print(df)
    #separate_data_into_date_and_data(df)
    #separate_data_by_years(df)
    #separate_data_by_weeks(df)
    print('ПОЛУЧЕНИЕ ДАННЫХ ПО ДАТЕ :')
    #print(get_data_by_date(df, datetime(2024, 1, 25)))

    #print('ВЫВОД next_data() :')
    #for index in range(0, len(df)):
    #    print(next_data(df, index))

    print('ВЫВОД ИТЕРАТОРА :')
    #iterator = Iterator(df)
    #for item in iterator:
    #    print(item)
    sys.exit(app.exec_())

