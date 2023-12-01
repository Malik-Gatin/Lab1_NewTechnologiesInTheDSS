import os
import requests
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from datetime import datetime
import time
from urllib.parse import urlparse, parse_qs

IMAGES_FIELDS = ['date', 'image_url', 'file_name', 'image_path']

# Настройка веб-драйвера
def configure_webdriver():
    # Настройки браузера (headless режим)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)

# Получение значения параметра запроса из URL
def get_query_parameter(url, parameter_name):
    parsed_url = urlparse(url)
    query_parameters = parse_qs(parsed_url.query)
    return query_parameters.get(parameter_name, [None])[0]

# Ожидание загрузки элементов на странице
def wait_for_element(driver, selector):
    wait = WebDriverWait(driver, 5)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    except Exception as e:
        logging.error(f"Ошибка ожидания элементов: {str(e)}")

# Создание папки для класса и файла CSV, если они не существуют
def create_class_directory(class_n: str, full_size:bool = None, csv_name:str = "") -> str:
    class_name = class_n
    try:
        if(full_size):
            class_name += "_full-size"
        elif(full_size!=None):
            class_name += "_thumb"
        # Создаем папку для класса, если она не существует
        class_dir = os.path.join("dataset", class_name)
        if not os.path.exists(class_dir):
            os.makedirs(class_dir)
            logging.info(f"Создана папка {class_name}")
        else:
            logging.info(f"Папка {class_name} уже существует")

        # Создаем файл CSV для класса, если он не существует
        if(csv_name!=""):
            csv_file_path = os.path.join(class_dir, f"{csv_name}.csv")
        else:
            csv_file_path = os.path.join(class_dir, f"{class_name}.csv")
        if not os.path.exists(csv_file_path):
            with open(csv_file_path, mode='w', newline='') as file:
                csv.writer(file)
            logging.info(f"Создан файл CSV для {class_name}")
        else:
            logging.info(f"Файл CSV уже существует для {class_name}")
        return csv_file_path
    except Exception as e:
        logging.error(f"Ошибка при создании файла или папки {class_name}: {str(e)}")  

# создание пути до файла .csv
def create_file_path(class_n:str, full_size:bool = None) -> str:
    class_name = class_n
    if(full_size):
        class_name += "_full-size"
    elif(full_size!=None):
        class_name += "_thumb"
    return os.path.join("dataset", class_name, f"{class_name}.csv")

# запись в .csv файл
def write_csv_file(path: str, data: list) -> None:
    mode = 'w' if not os.path.exists(path) else 'a'
    with open(path, mode, newline='') as csv_file:
      csv_writer = csv.writer(csv_file)
      csv_writer.writerow(data)

# Загрузка изображения
def download_image(img_url, img_path):
    max_retry = 2  # Максимальное количество попыток загрузки изображения
    for _ in range(max_retry):
        try:
            img_extension = img_url.split(".")[-1]
            img_ext = "jpg" in img_extension or "thumbs" in img_extension
            if img_ext:
                img_data = requests.get(img_url).content
                with open(img_path, "wb") as img_file:
                    img_file.write(img_data)         
                return True
        except Exception as e:
            logging.warning(f"Ошибка при загрузке изображения: {str(e)}")
    logging.error(f"Не удалось загрузить изображение: {img_url}")
    return False

# Загружает изображение по указанному URL-адресу
def download_images(query, num_images=1000, full_size=False):
    class_name = query

    create_class_directory(class_name, full_size)
    driver = configure_webdriver()
    # URL для поиска изображений
    url = f"https://yandex.ru/images/search?text={query}&type=photo"
    driver.get(url)

    count = 0
    csv_file_path = create_file_path(class_name, full_size)

    write_csv_file(csv_file_path, IMAGES_FIELDS)

    while count < num_images:
        # Выбор селектора для изображения (миниатюра или полноразмерное)
        img_selector = "img.serp-item__thumb" if not full_size else "a.serp-item__link"
        wait_for_element(driver, img_selector)
        img_links = driver.find_elements(By.CSS_SELECTOR, img_selector)

        for img_link in img_links:
            if count >= num_images:
                break
            try:
                if not full_size:
                    img_url = img_link.get_attribute("src")
                else:
                    img_url = img_link.get_attribute("href")
                    img_url = get_query_parameter(img_url, "img_url")

                if ("jpg" in img_url or "thumbs" in img_url):
                    filename = f"{count:04}.jpg"
                    img_path = os.path.join("dataset", class_name, filename)

                    if download_image(img_url, img_path):
                        count += 1
                        write_csv_file(csv_file_path, [datetime.now().strftime('%Y-%m-%d'), img_url, filename, img_path])
                    logging.info(f"Uploaded image {count} for class {class_name}")
                else:
                    continue
            except Exception as e:
                pass

        # Прокручиваем страницу вниз, чтобы подгрузились новые картинки
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
    # Завершаем сеанс браузера
    driver.quit()   