import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QFileDialog, QTableWidget, QTableWidgetItem, QSizePolicy, QDialog, QLabel
import pandas as pd
from datetime import datetime
from core.download_images import *
from core.work_with_data import *
from image_download_dialog import ImageDownloadDialog
from date_input_dialog import DateInputDialog
from image_display_dialog import ImageDisplayDialog
from info_display import TextDisplayWindow

class ImageDownloadApp(QMainWindow):
    
    df = None
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Download App")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        # Кнопка загрузки изображений из интернета
        self.start_button = QPushButton("Загрузка изображений")
        self.start_button.clicked.connect(self.start_download)
        self.layout.addWidget(self.start_button)

        # Кнопка выбора csv файла
        self.choose_file_button = QPushButton("Выбрать .csv файл")
        self.choose_file_button.clicked.connect(self.choose_csv_file)
        self.layout.addWidget(self.choose_file_button)
        
        # Таблица для отображения csv
        self.dataset_table = QTableWidget()
        self.layout.addWidget(self.dataset_table)

        # Кнопка разделения исходного датасета на даты и данные
        self.step1_button = QPushButton("Разделение датасета на даты и данные")
        self.step1_button.clicked.connect(self.step1_split_xy)
        self.layout.addWidget(self.step1_button)

        # Кнопка разделения исходного датасета по годам
        self.step2_button = QPushButton("Разделение датасета по годам")
        self.step2_button.clicked.connect(self.step2_split_yearly)
        self.layout.addWidget(self.step2_button)

        # Кнопка разделения исходного датасета по неделям
        self.step3_button = QPushButton("Разделение датасета по неделям")
        self.step3_button.clicked.connect(self.step3_split_weekly)
        self.layout.addWidget(self.step3_button)

        # Кнопка получения данных по определенной дате
        self.step4_button = QPushButton("Получить данные по дате")
        self.step4_button.clicked.connect(self.open_date_dialog)
        self.layout.addWidget(self.step4_button)
        
        # Метка для отображения изображения
        self.image_label = QLabel()
        self.layout.addWidget(self.image_label)

        # Кнопка просмотра данных
        self.show_image_button = QPushButton("Просмотреть данные")
        self.show_image_button.clicked.connect(self.show_image_dialog)
        self.layout.addWidget(self.show_image_button)

        self.central_widget.setLayout(self.layout)

        self.dataset = None

        # Устанавливаем политику изменения размера для central_widget
        self.central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # открываем форму загрузки изображений
    def start_download(self):
        self.image_download_dialog = ImageDownloadDialog(self)
        self.image_download_dialog.exec_()

    # выбор csv файла для отображения
    def choose_csv_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            self.load_dataset_from_local_file(file_name)
            dir = file_name.split('/')[-2]
            filen = file_name.split('/')[-1]
            if(filen.__contains__(dir)):
                self.df = create_data_frame_from_csv(file_name, IMAGES_FIELDS)
                write_another_dates(self.df, datetime(2023, 1, 1))
            self.show_text_window(f"Выбранный csv файл: {file_name}")  
            
    # форма отображения картинок с помощью итератора
    def show_image_dialog(self):
        try:
            # Создаем и отображаем диалоговое окно с изображением
            self.image_dialog = ImageDisplayDialog(self.df)
            self.image_dialog.exec_()
        except StopIteration:
            self.show_text_window("Картинки закончились!")   
            
    # форма информационных сообщений  
    def show_text_window(self, text:str):
        window = TextDisplayWindow(text)
        window.exec_()

    # загружаем датасет из выбранного локального файла
    def load_dataset_from_local_file(self, file_name):
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
            max_column_width = 500
            for col in range(self.dataset_table.columnCount()):
                current_width = self.dataset_table.columnWidth(col)
                if current_width > max_column_width:
                    self.dataset_table.setColumnWidth(col, max_column_width)
            # Измеряем ширину всех столбцов
            total_width = sum(self.dataset_table.columnWidth(col) for col in range(self.dataset_table.columnCount()))

            # Определяем высоту окна в зависимости от количества записей в таблице
            max_rows = 20
            height = min(len(self.dataset), max_rows) * 25 + 100  # Примерный размер строки: 25 пикселей

            # Устанавливаем ширину и высоту окна
            self.resize(total_width + 100, height)

        except Exception as e:
            self.show_text_window(f"Ошибка загрузки датасета: {str(e)}")
            self.dataset = None
            
    # форма выбора даты        
    def open_date_dialog(self):
        date_dialog = DateInputDialog(self)
        result = date_dialog.exec_()
        if result == QDialog.Accepted:
            date_input = date_dialog.get_date()
            self.step4_get_data_by_date(date_input)   

    # Разделяем данные по датам и данным
    def step1_split_xy(self):
        if self.dataset is not None:
            separate_data_into_date_and_data(self.df)
            self.show_text_window("Данные успешно разделены по датам и данным!")
            pass
        else:
            self.show_text_window("Сначала выберите CSV Файл!")

    # Разделяем данные по годам
    def step2_split_yearly(self):
        if self.dataset is not None:
            separate_data_by_years(self.df)
            self.show_text_window("Данные успешно разделены по годам!")
            pass
        else:
            self.show_text_window("Сначала выберите CSV Файл!")

    # Разделяем данные по неделям
    def step3_split_weekly(self):
        if self.dataset is not None:
            separate_data_by_weeks(self.df)
            self.show_text_window("Данные успешно разделены по неделям!")
            pass
        else:
            self.show_text_window("Сначала выберите CSV Файл!")

    # Получаем данные по введенной дате
    def step4_get_data_by_date(self, date_str):
        if self.dataset is not None:
            try:
                date_to_get = datetime.strptime(date_str, "%Y-%m-%d")
                data = get_data_by_date(self.df, date_to_get)
                if data is not None:
                    self.show_text_window(f"Данные за {date_to_get}: {data}")
                else:
                    self.show_text_window(f"Не существует данных для даты: {date_to_get}")
            except ValueError:
                self.show_text_window("Неверный формат данных. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")
        else:
            self.show_text_window("Сначала выберите CSV Файл!")
         

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageDownloadApp()
    window.show()
    sys.exit(app.exec_())

