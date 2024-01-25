import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QPushButton, QWidget, QFileDialog, QTableWidget, QTableWidgetItem, QSizePolicy, QLabel,  QStackedWidget
from data_processing import *
from info_display import TextDisplayWindow
from class_label_input_dialog import ClassLabelInputDialog
from data_input_dialog import DataInputDialog

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
        
        self.dataframe_label = QLabel("DataFrame: None")  # Изначально название DataFrame отображается как "None"
        self.layout.addWidget(self.dataframe_label)
        
        # Таблица для отображения csv
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
        self.step5_button.clicked.connect(self.step5_get_stats_dimensions)
        self.layout.addWidget(self.step5_button)

        # 6. Фильтрация по метке класса
        self.step6_button = QPushButton("Фильтрация по метке")
        self.step6_button.clicked.connect(self.step6_filter_by_class_label)
        self.layout.addWidget(self.step6_button)
        
        # 7. Фильтрация по метке класса и размерности
        self.step7_button = QPushButton("Фильтрация по метке и размеру")
        self.step7_button.clicked.connect(self.step7_filter_by_class_label_and_dimension)
        self.layout.addWidget(self.step7_button)
        # 8. Добавление количества пикселей
        self.step8_button = QPushButton("Добавление пикселей")
        self.step8_button.clicked.connect(self.step8_add_pixel_count)
        self.layout.addWidget(self.step8_button)
        
        # 9. Вычисление и вывод гистограмм по каждому каналу (R, G, B)
        self.step8_button = QPushButton("Вывод гистограмм")
        self.step8_button.clicked.connect(self.step9_get_random_image_histogram)
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

            self.load_dataframe(create_data_frame_from_csv(file_path = annotation_file, fields=ANNOTATION_FIELDS), ANNOTATION_DIRECTORY)
            print(f"\nШаг 1-2. Создан и проверен на ошибки объект DataFrame")
            self.show_text_window(f"Выбранный csv файл: {file_name}")  
            
    # форма информационных сообщений  
    def show_text_window(self, text:str):
        window = TextDisplayWindow(text)
        window.exec_()

    def switch_dataframe(self):
        if len(self.dataframes) > 1:
            dataframe_names = list(self.dataframes.keys())
            current_index = dataframe_names.index(self.current_dataframe)
            next_index = (current_index + 1) % len(dataframe_names)
            next_dataframe_name = dataframe_names[next_index]

            # Переключаем QStackedWidget на новую таблицу
            self.dataset_table.setCurrentWidget(self.tables[next_dataframe_name])
            self.current_dataframe = next_dataframe_name
            self.dataframe_label.setText(f"DataFrame: {next_dataframe_name}")
            self.update_window_size()   
            
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

        # Добавляем таблицу в QStackedWidget
        table_index = self.dataset_table.addWidget(table)
        self.current_dataframe = table_name
        self.dataframe_label.setText(f"DataFrame: {table_name}")
        self.tables[table_name] = table
        self.dataset_table.setCurrentIndex(table_index)
        self.update_window_size()   
        
    def update_window_size(self):
        current_table = self.dataset_table.currentWidget()
        if current_table is not None:
            # Определение высоты таблицы в зависимости от количества записей
            max_rows = 10
            table_height = min(current_table.rowCount(), max_rows) * 40 + 350
            table_width = current_table.columnCount() * 250 + 200
            if(current_table.columnCount() > 3):
                table_width = current_table.columnCount() * 180
            # Установка размеров окна
            self.resize(table_width, table_height)

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
            
    # Получение статистики по размерности и по сумме меток класса
    def step5_get_stats_dimensions(self):
        if self.dataframes[ANNOTATION_DIRECTORY] is not None:
            image_stats = calculate_image_stats(self.dataframes[ANNOTATION_DIRECTORY])
            self.load_dataframe(image_stats, STATS_DIMENSION)
            self.show_text_window("Получена статистика по размерности изображений!")
            class_label_sum = calculate_class_label_sum(self.dataframes[ANNOTATION_DIRECTORY])
            self.load_dataframe(class_label_sum, STATS_SUM_IMAGES)
            self.show_text_window("Получена статистика по сумме меток классов!")
            # Гистограмма распределения по меткам
            plot_class_label_distribution(class_label_sum)
            pass
        else:
            self.show_text_window("Сначала выберите CSV Файл!")         
    
    # Получение статистики по размерности и по сумме меток класса
    def step6_filter_by_class_label(self):
        if self.dataframes[ANNOTATION_DIRECTORY] is not None:
            dialog = ClassLabelInputDialog()
            if dialog.exec_():
                class_label = dialog.result_label
                filtered_data = filter_by_class_label(self.dataframes[ANNOTATION_DIRECTORY], label = class_label)
                self.load_dataframe(filtered_data, FILTER_LABEL)
                self.show_text_window(f"Датасет отфильтрован по метке класса = {class_label} !")
                pass
        else:
            self.show_text_window("Сначала выберите CSV Файл!")       
            
    # Получение статистики по размерности и по сумме меток класса
    def step7_filter_by_class_label_and_dimension(self):
        if self.dataframes[ANNOTATION_DIRECTORY] is not None:
            dialog = DataInputDialog()
            if dialog.exec_() == QDialog.Accepted:
                class_label = dialog.class_label
                width = dialog.width
                height = dialog.height
                filtered_data = filter_by_dimensions_and_class(self.dataframes[ANNOTATION_DIRECTORY], label = class_label, max_width = width, max_height = height)
                self.load_dataframe(filtered_data, FILTRER_DIMENSION)
                self.show_text_window(f"Датасет отфильтрован по метке класса и размерностям!")
                pass
        else:
            self.show_text_window("Сначала выберите CSV Файл!")     
            
    # Добавление размерности в DataFrame
    def step8_add_pixel_count(self):
        if self.dataframes[ANNOTATION_DIRECTORY] is not None:
            add_pixel_count(self.dataframes[ANNOTATION_DIRECTORY])
            self.load_dataframe(self.dataframes[ANNOTATION_DIRECTORY], ANNOTATION_DIRECTORY)
            self.show_text_window("Добавлен столбец с количеством пикселей!")
            pixel_statistics = calculate_pixel_stats(self.dataframes[ANNOTATION_DIRECTORY])
            self.load_dataframe(pixel_statistics, STATS_PIXEL)
            self.show_text_window("Получена статистика по количеству пикселей!")
            dialog = ClassLabelInputDialog()
            if dialog.exec_():
                plot_sample_images(self.dataframes[ANNOTATION_DIRECTORY], label =  dialog.result_label)
            pass
        else:
            self.show_text_window("Сначала выберите CSV Файл!")

    def step9_get_random_image_histogram(self):
        if self.dataframes[ANNOTATION_DIRECTORY] is not None:
            dialog = ClassLabelInputDialog()
            if dialog.exec_():
                histograms = get_random_image_histogram(self.dataframes[ANNOTATION_DIRECTORY], dialog.result_label)
                plot_histograms(histograms)
            pass
        else:
            self.show_text_window("Сначала выберите CSV Файл!")            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageDownloadApp()
    window.show()
    sys.exit(app.exec_())

