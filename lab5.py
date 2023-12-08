import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QFileDialog, QTableWidget, QTableWidgetItem, QSizePolicy, QLabel,  QStackedWidget
import pandas as pd
from datetime import datetime
from data_processing import *
from info_display import TextDisplayWindow

class ImageDownloadApp(QMainWindow):
    df = None
    def __init__(self):
        super().__init__()

        # Создаем словарь для хранения DataFrame и соответствующих таблиц
        self.dataframes = {}
        self.tables = {}
        self.current_dataframe = None  # Текущий отображаемый DataFrame

        self.setWindowTitle("Lab5 App")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        # Кнопка выбора csv файла
        self.choose_file_button = QPushButton("Выбрать .csv файл")
        self.choose_file_button.clicked.connect(self.choose_csv_file)
        self.layout.addWidget(self.choose_file_button)
        
        # Добавляем кнопку переключения между таблицами
        self.switch_dataframe_button = QPushButton("Переключить DataFrame")
        self.switch_dataframe_button.clicked.connect(self.switch_dataframe)
        self.layout.addWidget(self.switch_dataframe_button)
        
        # Таблица для отображения csv
        #self.dataset_table = QTableWidget()
        #self.layout.addWidget(self.dataset_table)
        self.dataset_table= QStackedWidget()
        self.layout.addWidget(self.dataset_table)

        # 3. Добавить в DataFrame столбец, который будет содержать числовую метку 0 для первого класса, 1 для второго класса.
        self.step3_button = QPushButton("Добавление числовой метки")
        self.step3_button.clicked.connect(self.step3_add_numeric_label)
        self.layout.addWidget(self.step3_button)

        # 4. Добавить в DataFrame три столбца, первый из которых содержит информацию о высоте изображения, второй о ширине, а третий о глубине (количество каналов).
        self.step4_button = QPushButton("Добавление размерности")
        self.step4_button.clicked.connect(self.step4_add_image_dimensions)
        self.layout.addWidget(self.step4_button)

        # 5. Вычисление статистики
        self.step5_button = QPushButton("Вычисление статистики по размерности")
        self.step5_button.clicked.connect(self.step3_add_numeric_label)
        self.layout.addWidget(self.step5_button)

        # 6. Фильтрация по метке класса
        self.step6_button = QPushButton("Фильтрация по метке")
        self.step6_button.clicked.connect(self.step3_add_numeric_label)
        self.layout.addWidget(self.step6_button)
        
        # 7. Фильтрация по метке класса и размерности
        self.step7_button = QPushButton("Фильтрация по метке и размеру")
        self.step7_button.clicked.connect(self.step3_add_numeric_label)
        self.layout.addWidget(self.step7_button)
        # 8. Добавление количества пикселей
        self.step8_button = QPushButton("Добавление пикселей")
        self.step8_button.clicked.connect(self.step3_add_numeric_label)
        self.layout.addWidget(self.step8_button)
        
        # Метка для отображения изображения
        self.image_label = QLabel()
        self.layout.addWidget(self.image_label)

        self.central_widget.setLayout(self.layout)

        self.dataset = None

        # Устанавливаем политику изменения размера для central_widget
        self.central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # выбор csv файла для отображения
    def choose_csv_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            dir = file_name.split('/')[-2]
            filen = file_name.split('/')[-1]
            annotation_file = os.path.join(dir, filen)
            print(f"Датасет успешно скопирован и переименован в {dir}")
            print(f"Создан Файл-аннотация: {filen}")
            
            # Создаем объект DataFrame 
            self.df = create_data_frame_from_csv(file_path = annotation_file, fields=ANNOTATION_FIELDS)
            self.load_dataframe(create_data_frame_from_csv(file_path = annotation_file, fields=ANNOTATION_FIELDS), ANNOTATION_DIRECTORY)
            #self.load_dataset_from_dataframe(self.df)
            print(f"\nШаг 1-2. Создан и проверен на ошибки объект DataFrame")
            self.show_text_window(f"Выбранный csv файл: {file_name}")  
            
    # форма информационных сообщений  
    def show_text_window(self, text:str):
        window = TextDisplayWindow(text)
        window.exec_()

    def switch_dataframe(self):
        # Пример переключения между таблицами при нажатии на кнопку
        if len(self.dataframes) > 1:
            # Если есть больше одного DataFrame в словаре, переключаемся на следующий
            dataframe_names = list(self.dataframes.keys())
            current_index = dataframe_names.index(self.current_dataframe)
            next_index = (current_index + 1) % len(dataframe_names)
            next_dataframe_name = dataframe_names[next_index]

            # Убираем текущую таблицу
            self.layout.removeWidget(self.tables[self.current_dataframe])
            self.tables[self.current_dataframe].deleteLater()

            # Добавляем новую таблицу
            self.layout.addWidget(self.tables[next_dataframe_name])
            self.current_dataframe = next_dataframe_name 
            
    def load_dataframe(self, dataframe, table_name):
        # Сохраняем DataFrame в словаре
        self.dataframes[table_name] = dataframe

        # Очищаем таблицу перед добавлением новых данных
        table = QTableWidget()
        table.setRowCount(0)
        table.setColumnCount(len(dataframe.columns))
        table.setHorizontalHeaderLabels(dataframe.columns)

        # Заполняем таблицу данными
        for row in range(len(dataframe)):
            table.insertRow(row)
            for col in range(len(dataframe.columns)):
                item = QTableWidgetItem(str(dataframe.iloc[row, col]))
                table.setItem(row, col, item)

        # Динамически регулируем ширину столбцов
        table.resizeColumnsToContents()
        self.update_window_size()   

        # Добавляем таблицу в QStackedWidget
        table_index = self.dataset_table.addWidget(table)
        self.dataset_table.setCurrentIndex(table_index)
        
    def update_window_size(self):
        current_table = self.dataset_table.currentWidget()
        if current_table is not None:
            # Определение высоты таблицы в зависимости от количества записей
            max_rows = 20
            table_height = min(current_table.rowCount(), max_rows) * 25 + 100
            
            # Установка размеров окна
            self.resize(self.width(), table_height)
         
    # загружаем датасет из объекта DataFrame     
    def load_dataset_from_dataframe(self, df):
        try:
            self.df = df
                
            # Очистка QTableWidget перед добавлением новых данных
            self.dataset_table.clear()
            self.dataset_table.setRowCount(0)
            self.dataset_table.setColumnCount(len(self.df.columns))

            # Установка заголовков столбцов
            self.dataset_table.setHorizontalHeaderLabels(self.df.columns)

            # Заполнение таблицы данными из DataFrame
            for row in range(len(self.df)):
                self.dataset_table.insertRow(row)
                for col in range(len(self.df.columns)):
                    item = QTableWidgetItem(str(self.df.iloc[row, col]))
                    self.dataset_table.setItem(row, col, item)

            # Динамическое изменение размеров столбцов
            self.dataset_table.resizeColumnsToContents()
            max_column_width = 550
            for col in range(self.dataset_table.columnCount()):
                current_width = self.dataset_table.columnWidth(col)
                if current_width > max_column_width:
                    self.dataset_table.setColumnWidth(col, max_column_width)
            # Измерение ширины всех столбцов
            total_width = sum(self.dataset_table.columnWidth(col) for col in range(self.dataset_table.columnCount()))

            # Определение высоты окна в зависимости от количества записей в таблице
            max_rows = 20
            height = min(len(self.df), max_rows) * 25 + 100  # Примерный размер строки: 25 пикселей

            # Установка размеров окна
            self.resize(total_width + 100, height)

        except Exception as e:
            self.show_text_window(f"Ошибка загрузки датасета: {str(e)}")
            self.df = None  

    # Добавление числовой метки в DataFrame
    def step3_add_numeric_label(self):
        
        if self.dataframes[ANNOTATION_DIRECTORY] is not None:
            add_numeric_label(self.dataframes[ANNOTATION_DIRECTORY])
            #self.load_dataset_from_dataframe(self.df)
            self.load_dataframe(self.dataframes[ANNOTATION_DIRECTORY], ANNOTATION_DIRECTORY)
            self.show_text_window("Добавлен столбец с числовыми метками!")
            pass
        else:
            self.show_text_window("Сначала выберите CSV Файл!")
            
    # Добавление размерности в DataFrame
    def step4_add_image_dimensions(self):
        if self.dataframes[ANNOTATION_DIRECTORY] is not None:
            add_image_dimensions(self.dataframes[ANNOTATION_DIRECTORY])
            self.load_dataframe(self.dataframes[ANNOTATION_DIRECTORY], ANNOTATION_DIRECTORY)
            self.show_text_window("Добавлены столбцы с размерностями!")
            pass
        else:
            self.show_text_window("Сначала выберите CSV Файл!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageDownloadApp()
    window.show()
    sys.exit(app.exec_())

