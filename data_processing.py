import pandas as pd
import os
import csv
import shutil
import random
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2

IMAGES_FIELDS = ['date', 'image_url', 'file_name', 'file_path']
ANNOTATION_FIELDS = ['absolute_path', 'class_label']
ANNOTATION_DIRECTORY = "dataset_annotations"
STATS_DIMENSION = "stats_dimension"
STATS_PIXEL = "stats_pixel"
FILE_NAME_ANNOTATION = "dataset_annotations.csv"
DATASET_DIRECTORY = "dataset"
IMAGE_STATS = ['image_height', 'image_width', 'image_channels']


# Копирует файлы из датасета в другую директорию, переименовывая их случайным номером и создает файл аннотацию.
# dataset_directory: Путь к папке с датасетом
# output_directory: Путь куда будет скопирован датасет
def copy_and_rename_dataset_with_annotation(dataset_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Создаем CSV-файл для аннотаций
    annotation_file = os.path.join(output_directory, FILE_NAME_ANNOTATION)
    with open(annotation_file, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(ANNOTATION_FIELDS)

        for root, _, files in os.walk(dataset_directory):
            for file in files:
                # Получаем путь к файлу
                path = os.path.join(root, file)

                # Получаем метку класса (имя папки)
                class_label = os.path.basename(root)

                random_number = random.randint(0, 10000)

                # Создаем новое имя файла с номером и расширением .jpg
                new_filename = f"{random_number}.jpg"

                # Полный путь к новому файлу в выходной директории
                new_file_path = os.path.join(output_directory, new_filename)

                # Копируем файл и переименовываем
                shutil.copy(path, new_file_path)

                # Получаем абсолютный путь к новому файлу
                absolute_path = os.path.abspath(new_file_path)

                # Записываем информацию о файле в CSV-файл
                csv_writer.writerow([absolute_path, class_label])

# проверка на существование полей в .csv файле
def check_csv_on_valid_fields(df: pd.DataFrame, required_fields: list) -> bool:
    for field in required_fields:
        if field not in df.columns:
            return False
    return True


#  Читает данные из файла в формате CSV, выполняет проверку наличия необходимых полей и объединяет их в один DataFrame.
def create_data_frame_from_csv(file_path: str, fields: list) -> pd.DataFrame:
    df_list = []
    data = pd.read_csv(file_path)
    # Именование колонок
    # Проверка наличия необходимых полей в данных
    if not check_csv_on_valid_fields(data, fields):
        print(f'Ошибка: Файл {file_path} не содержит какого-то из необходимых полей {fields}')
        return pd.DataFrame()  # Возвращаем пустой DataFrame при отсутствии обязательных полей
    df_list.append(data)
    df = pd.concat(df_list, ignore_index=True)
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    return df

# 3. Добавить в DataFrame столбец, который будет содержать числовую метку 0 для первого
# класса, 1 для второго класса. Через словарь или Categoriacal
def add_numeric_label(df):
    # Получаем уникальные классы из столбца column_name
    unique_classes = df['class_label'].unique()

    # Создаем словарь для отображения классов в числовые метки
    class_labels = {class_name: i for i, class_name in enumerate(unique_classes)}

    # Добавляем числовую метку в DataFrame
    df['numeric_label'] = df['class_label'].map(class_labels)

# 4. Добавить в DataFrame три столбца, первый из которых содержит информацию
# о высоте изображения, второй о ширине, а третий о глубине (количество каналов).
def add_image_dimensions(df):
    # Получаем размеры изображений для каждого пути к файлу
    dimensions = df['absolute_path'].apply(get_image_dimensions)

    # Разделяем результат на три столбца: высота, ширина, глубина
    df[['image_height', 'image_width', 'image_channels']] = pd.DataFrame(dimensions.tolist(), index=df.index)

# Получаем размерность изображений и глубину
def get_image_dimensions(file_path):
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            if img.mode == 'RGB':
                channels = 3
            elif img.mode == 'RGBA':
                channels = 4
            else:
                channels = 1  # Примерное количество каналов для других режимов изображений
            return width, height, channels
    except:
        print(f'Ошибка при получении размеров изображения {file_path}')
        return None

# 5. С использованием Pandas вычислить статистическую информацию для столбцов,
# содержащих информацию о размерах изображения (ширина, высота, глубина) и метках класса.
# Describe. Для меток - табличку с суммой по метке, построить гистограмму или pie.
# На основе полученной информации определить, является ли собранный вами набор сбалансированным 
# (на основе статистической информации о столбце с метками класса). Баланс по числу элементов в каждом классе.
    
def calculate_image_stats(df):
    # Статистика для столбцов с размерами изображений
    image_stats = df[IMAGE_STATS].describe()
    return image_stats

def calculate_class_label_sum(df):
    # Сумма по меткам класса
    class_label_sum = df['class_label'].value_counts()
    return class_label_sum    

def plot_class_label_distribution(class_label_sum):
    # Построение гистограммы для суммы по меткам класса
    ax = class_label_sum.plot(kind='bar', figsize=(10, 6))
    plt.xlabel('Метка класса')
    plt.ylabel('Количество')
    plt.title('Количество элементов по классам')
    
    ax.set_xticklabels(class_label_sum.index, rotation=45, ha='right')  # Поворот меток оси x
    
    plt.tight_layout()  # Улучшение компоновки, чтобы избежать обрезки изображения
    plt.show()

# 6. Написать функцию, которая на вход принимает DataFrame и метку класса,
# а возвращает отфильтрованны по метке DataFrame. Условие фильтрации - в новый
# DataFrame включаются те строки, для которых значение метки соответсвует заданному.
def filter_by_class_label(df, label):
    if(isinstance(label, int)):
        filtered_df = df[df['numeric_label'] == label].copy()
    elif(isinstance(label, str)):
        filtered_df = df[df['class_label'] == label].copy()
    return filtered_df

# 7. Написать функцию, которая на вход принимает метку класса, максимальное значение ширины
# и максимальное значение высоты изображения, а возвращает отфильтрованный по заданным параметрам DataFrame.
# Условие фильтрации - в новый DataFrame включаются те строки, для которых размеры удовлетворяют следующему условию:
# height  ≤  max_height and width  ≤  max_width, а метка класса соответствует указанной.
def filter_by_dimensions_and_class(df, label, max_width, max_height):
    if(isinstance(label, int)):
        filter_label = 'numeric_label'

    elif(isinstance(label, str)):   
        filter_label = 'class_label'
        
    filtered_df = df[(df[filter_label] == label) & 
                     (df['image_width'] <= max_width) & 
                     (df['image_height'] <= max_height)].copy()    
    return filtered_df

# 8. Выполнить группировку DataFrame по метке класса с вычислением максимального, минимального и среднего значения
# по количеству пикселей (необходимо будет добавить новый столбец, значение для которого вычисляется по уже заполненным столбцам.
# О подсчете количества пикселей говорилось на лекции OpenCV). Распознавание изображений. *Построить график 3-5 изображений.
def add_pixel_count(df):
    # Добавляет столбец с количеством пикселей в DataFrame
    df['pixel_count'] = df['image_height'] * df['image_width']
    return df

def calculate_pixel_stats(df):
    # Вычисляет статистику по количеству пикселей для каждой метки класса
    pixel_stats = df.groupby('class_label')['pixel_count'].agg(['max', 'min', 'mean'])
    return pixel_stats

def plot_sample_images(df, label, num_images=5):
    filtered_df = filter_by_class_label(df, label)
    sample_images = filtered_df.head(num_images).reset_index(drop=True)
    
    fig, axes = plt.subplots(1, len(sample_images), figsize=(15, 5))
    
    for idx, row in sample_images.iterrows():
        img_path = row['absolute_path']  # Путь к изображению
        img = plt.imread(img_path)
        axes[idx].imshow(img)
        axes[idx].axis('off')
        axes[idx].set_title(row['class_label'])  # Метка класса
        
    plt.tight_layout()
    plt.show()
    
# 9. Написать функцию, которая с использованием средств библиотеки OpenCV строит гистограмму. 
# На вход функция принимает DataFrame и метку класса, на выходе - три массива 
# (каждый массив соответствует значениям гистограммы по каждому каналу). 
# Выбор изображения из DataFrame, для которого будет строиться гистограмма, сделать случайным (numpy или аналогичные для random).

def get_random_image(df, class_label):
    # Фильтрация DataFrame по метке класса
    class_images = filter_by_class_label(df, class_label)

    # Выбор случайного изображения
    random_index = np.random.randint(0, len(class_images))
    return class_images.iloc[random_index]['absolute_path']

def get_random_image_histogram(df, class_label):
    random_image_path = get_random_image(df, class_label)

    # Загрузка изображения с помощью OpenCV
    image = cv2.imread(random_image_path)

    # Разделение изображения на каналы
    b, g, r = cv2.split(image)

    # Вычисление гистограмм для каждого канала
    hist_r = cv2.calcHist([r], [0], None, [256], [0, 256])
    hist_g = cv2.calcHist([g], [0], None, [256], [0, 256])
    hist_b = cv2.calcHist([b], [0], None, [256], [0, 256])
    print ("\nВыбранное изображение для гистограммы:\n" + random_image_path)
    return [hist_r, hist_g, hist_b]

# 10. С использованием средств библиотеки matplotlib или seaborn выполнить отрисовку гистограмм,
# которые возвращаются из функции пункта 9. Графики и оси должны иметь соответствующие подписи.
def plot_histograms(histograms):
    channels = ['R', 'G', 'B']
    colors = ['red', 'green', 'blue']
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for i, channel in enumerate(channels):
        axes[i].hist(histograms[i], bins=256, color=colors[i], alpha=0.7)
        axes[i].set_title(f'Гистограмма для канала {channel}')
        axes[i].set_xlabel('Интенсивность пикселей')
        axes[i].set_ylabel('Частота')
    
    plt.tight_layout()
    plt.show()

def main():
    pd.set_option('display.max_colwidth', None)
    # 1-2. Создаем файл-аннотацию и формируем объект DataFrame
    copy_and_rename_dataset_with_annotation(DATASET_DIRECTORY, ANNOTATION_DIRECTORY)
    annotation_file = os.path.join(ANNOTATION_DIRECTORY, FILE_NAME_ANNOTATION)
    print(f"Датасет успешно скопирован и переименован в {ANNOTATION_DIRECTORY}")
    print(f"Создан Файл-аннотация: {FILE_NAME_ANNOTATION}")
    
    class_name = 'tiger_thumb'
    
    # Создаем объект DataFrame 
    df = create_data_frame_from_csv(file_path = annotation_file, fields=ANNOTATION_FIELDS)
    print(f"\nШаг 1-2. Создан и проверен на ошибки объект DataFrame:\n{df}\n")
    
    # 3. Добавление столбца с числовыми метками
    add_numeric_label(df, 'class_label')
    print(f"\nШаг 3. Добавлен столбец с числовыми метками:\n{df}\n")
    
    # 4. Добавление столбцов с размерностью изображения
    add_image_dimensions(df)
    print(f"\nШаг 4. Добавление столбцов с размерностью изображения:\n{df}\n")
    
    # 5. Вывод статистической информации
    image_stats = calculate_image_stats(df)
    class_label_sum = calculate_class_label_sum(df)
    print(f"\nШаг 5.")
    print(f"Статистика для размеров изображений:\n{image_stats}")
    print(f"\nСумма по меткам класса:\n{class_label_sum}\n")
    # Гистограмма распределения по меткам
    plot_class_label_distribution(class_label_sum)
    
    # Выбираем метку для фильтрации
    label = 0 # можно также прописать строкой "leopard_thumb"
    
    # 6. Фильтрация по метке класса
    filtered_data = filter_by_class_label(df, label = label)
    print(f"\nШаг 6. Фильтрация по метке класса ({label}):\n{filtered_data}\n")
    
    # 7. Фильтрация по метке класса, ширине, и высоте изображения
    max_width = 300
    max_height = 480
    filtered_data = filter_by_dimensions_and_class(df, label = label,  max_width = max_width, max_height = max_height)
    print(f"\nШаг 7. Фильтрация по метке класса ({label}), ширине (до {max_width}), и высоте (до {max_height}) изображения:\n{filtered_data}\n")
    
    # 8. Группировка по кол-ву пикселей
    # Добавляем столбец с количеством пикселей
    df_with_pixels = add_pixel_count(df)
    print(f"\nШаг 8. Добавлен столбец с кол-вом пикселей:\n{df}\n")
    # Вычисляем статистику по количеству пикселей
    pixel_statistics = calculate_pixel_stats(df_with_pixels)
    print(f"\nШаг 8. Вычисляем статистику по кол-ву пикселей:\n{pixel_statistics}\n")
    # Построим график нескольких изображений
    plot_sample_images(df, label = class_name)
    
    # 9-10. Вычисление и вывод гистограмм по каждому каналу (R, G, B)
    histograms = get_random_image_histogram(df, class_name)
    plot_histograms(histograms)
    
# Вызов функции main
if __name__ == "__main__":
    main()