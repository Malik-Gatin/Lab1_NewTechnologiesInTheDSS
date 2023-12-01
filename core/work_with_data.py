import sys
sys.path.append('C:/Users/gatin/Desktop/MalikMagistracy/NewTechnologiesInDSS/lab3/core')
import pandas as pd
from datetime import datetime
from typing import Union
from download_images import *

IMAGES_FIELDS = ['date', 'image_url', 'file_name', 'image_path']

# проверка на существование полей в .csv файле
def check_csv_on_valid_fields(df: pd.DataFrame, required_fields: list) -> bool:
    for field in required_fields:
        if field not in df.columns:
            return False
    return True
     
#  Читает данные из файла в формате CSV, выполняет проверку наличия необходимых полей и объединяет их в один DataFrame.
def create_data_frame_from_csv(file: list, fields: list) -> pd.DataFrame:
    df_list = []
    data = pd.read_csv(file)
      # Проверка наличия необходимых полей в данных
    if check_csv_on_valid_fields(data, fields):
        data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
        df_list.append(data)
    else:
        print(f'Ошибка: Файл {file} не содержит необходимых полей')
    df = pd.concat(df_list, ignore_index=True)
    return df
     
# ШАГ 1
# Написать скрипт, который разобъёт исходный csv файл на файл X.csv и Y.csv, 
# с одинаковым количеством строк. Первый будет содержать даты, второй - данные.

# Запись других дат в .csv файл
def write_another_dates(df: pd.DataFrame, start_date: datetime) -> pd.DataFrame:
    df['date'] = [start_date + pd.DateOffset(days=i) for i in range(len(df))]
    return df

# Разделение данных на 2 .csv файла: с датами и остальными данными
def separate_data_into_date_and_data(df: pd.DataFrame) -> None:
    df_date = df['date']
    df_data = df.drop('date', axis=1)
    dir_x = create_class_directory(class_n="csv_date_by_data",csv_name="X")
    dir_y = create_class_directory(class_n="csv_date_by_data",csv_name="Y")
    df_date.to_csv(dir_x, index=False)
    df_data.to_csv(dir_y, index=False)

# ШАГ 2 
# Написать скрипт, который разобъёт исходный csv файл на N файлов, где каждый
# отдельный файл будет соответствовать одному году. Файлы называются по первой
# и последней дате, которую они содержат. (если файл содержит данные с первого
# января 2001 по 31 декабря 2001, то файл назвать 20010101_20011231.csv)

# Разделение данных на N .csv файлов по годам
def separate_data_by_years(df: pd.DataFrame) -> None:
    df['date'] = pd.to_datetime(df['date'])

    for year, group in df.groupby(df['date'].dt.year):
        start_date = group['date'].min().strftime('%Y%m%d')
        end_date = group['date'].max().strftime('%Y%m%d')
        filename = f'{start_date}_{end_date}'
        dir = create_class_directory(class_n='csv_years', csv_name=filename)
        group.to_csv(dir, index=False)

# ШАГ 3
# Написать скрипт, который разобъёт исходный csv файл на N файлов, где каждый
# отдельный файл будет соответствовать одной неделе. Файлы называются по первой
# и последней дате, которую они содержат.

# Разделение данных на N .csv файлов по неделям
def separate_data_by_weeks(df: pd.DataFrame) -> None:
    df['date'] = pd.to_datetime(df['date'])

    for (year, week), group in df.groupby([df['date'].dt.isocalendar().year, df['date'].dt.isocalendar().week]):
        start_date = group['date'].min().strftime('%Y%m%d')
        end_date = group['date'].max().strftime('%Y%m%d')
        filename = f'{start_date}_{end_date}'
        dir = create_class_directory(class_n='csv_weeks', csv_name=filename)
        group.to_csv(dir, index=False)

# Шаг 4 Написать скрипт, содержащий функцию, принимающую на вход дату 
# (тип datetime) и возвращающий данные для этой даты (из файла) или
#  None если данных для этой даты нет.
def get_data_by_date(df: pd.DataFrame, date: datetime) -> Union[None, pd.DataFrame]:
    data = df[df['date'] == date]
    if data.empty:
        return None
    else:
        return data.drop(columns=['date'])
