import pandas as pd
import os
import csv
import shutil
import random
from PIL import Image

IMAGES_FIELDS = ['date', 'image_url', 'file_name', 'file_path']
ANNOTATION_FIELDS = ['absolute_path', 'class_labell']
OUTPUT_FOLDER = "dataset_annotations"
CSV_FILE_NAME = "dataset_annotations.csv"
DATASET_FOLDER = "dataset"

def copy_and_rename_dataset_with_annotation(dataset_folder, output_folder):
    """
    Копирует файлы из датасета в другую директорию, переименовывая их случайным номером и создает файл аннотацию.

    :param dataset_folder: Путь к папке с датасетом
    :param output_folder: Путь куда будет скопирован датасет
    :return:
    """

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Создаем CSV-файл для аннотаций
    annotation_file = os.path.join(output_folder, CSV_FILE_NAME)
    with open(annotation_file, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(ANNOTATION_FIELDS)

        for root, _, files in os.walk(dataset_folder):
            for file in files:
                # Получаем путь к файлу
                path = os.path.join(root, file)

                # Получаем метку класса (имя папки)
                class_label = os.path.basename(root)

                random_number = random.randint(0, 10000)

                # Создаем новое имя файла с номером и расширением .jpg
                new_filename = f"{random_number}.jpg"

                # Полный путь к новому файлу в выходной директории
                new_file_path = os.path.join(output_folder, new_filename)

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
    if check_csv_on_valid_fields(data, fields):
        print(f'Ошибка: Файл {file_path} не содержит какого-то из необходимых полей {fields}')
        return pd.DataFrame()  # Возвращаем пустой DataFrame при отсутствии обязательных полей
    if 'date' in data.columns:
        try:
            data['date'] = pd.to_datetime(data['date'])
        except:
            print(f'Ошибка преобразования даты в файле {file_path}')
    df_list.append(data)
    df = pd.concat(df_list, ignore_index=True)
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    return df

# 3. Добавить в DataFrame столбец, который будет содержать числовую метку 0 для первого
# класса, 1 для второго класса. Через словарь или Categoriacal
def add_numeric_label(df, column_name):
    # Получаем уникальные классы из столбца column_name
    unique_classes = df[column_name].unique()

    # Создаем словарь для отображения классов в числовые метки
    class_labels = {class_name: i for i, class_name in enumerate(unique_classes)}

    # Добавляем числовую метку в DataFrame
    df['numeric_label'] = df[column_name].map(class_labels)

#4. Добавить в DataFrame три столбца, первый из которых содержит информацию
# о высоте изображения, второй о ширине, а третий о глубине (количество каналов).
def add_image_dimensions(df):
    # Получаем размеры изображений для каждого пути к файлу
    dimensions = df['absolute_path'].apply(get_image_dimensions)

    # Разделяем результат на три столбца: высота, ширина, глубина
    df[['image_height', 'image_width', 'image_channels']] = pd.DataFrame(dimensions.tolist(), index=df.index)

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

def main():
    pd.set_option('display.max_colwidth', None)
    #copy_and_rename_dataset_with_annotation(DATASET_FOLDER, OUTPUT_FOLDER)
    annotation_file = os.path.join(OUTPUT_FOLDER, CSV_FILE_NAME)
    df = create_data_frame_from_csv(file_path = annotation_file, fields=ANNOTATION_FIELDS)

    print(f"Датасет успешно скопирован и переименован в {OUTPUT_FOLDER}")

    print(f"Файл-аннотация создан: {CSV_FILE_NAME}")
    add_numeric_label(df, 'class_label')
    add_image_dimensions(df)
    print(df)
# Вызов функции main
if __name__ == "__main__":
    main()