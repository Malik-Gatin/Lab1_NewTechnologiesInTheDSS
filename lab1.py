import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
from urllib.parse import urlparse, parse_qs

# Создаем папку "dataset", если она не существует
if not os.path.exists("dataset"):
    os.mkdir("dataset")

# Создание папки для класса, если она не существует
def create_class_directory(class_name):
    # Создаем папку для класса, если она не существует
    class_dir = os.path.join("dataset", class_name)
    try:
        if not os.path.exists(class_dir):
            os.mkdir(class_dir)
    except Exception as e:
        logging.error(f"Error when creating a folder {class_name}: {str(e)}")    

# Настройка веб-драйвера
def configure_webdriver():
    # Настройки браузера (headless режим)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)

# Ожидание загрузки элементов на странице
def wait_for_element(driver, selector):
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    except Exception as e:
        logging.error(f"Ошибка ожидания элементов: {str(e)}")

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

# Получение значения параметра запроса из URL
def get_query_parameter(url, parameter_name):
    parsed_url = urlparse(url)
    query_parameters = parse_qs(parsed_url.query)
    return query_parameters.get(parameter_name, [None])[0]

# Загружает изображение по указанному URL-адресу
def download_images(query, num_images=1000, full_size=False):
    class_name = query
    if(full_size):
        class_name += "_full-size"
    else:
        class_name += "_thumb"

    create_class_directory(class_name)
    driver = configure_webdriver()

    # URL для поиска изображений
    url = f"https://yandex.ru/images/search?text={query}&type=photo"
    driver.get(url)

    count = 0

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

                    while not download_image(img_url, img_path):
                        # Если загрузка не удалась, попытаемся скачать следующую картинку
                        continue

                    count += 1
                    logging.info(f"Uploaded image {count} for class {class_name}")
                else:
                    continue
            except Exception as e:
                pass

        try:
            # Прокручиваем страницу вниз, чтобы увидеть кнопку "Далее"
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            next_button = driver.find_element(By.CSS_SELECTOR, "a.serp-advanced__item")
            if next_button:
                next_button.click()
                time.sleep(2)
        except Exception as e:
            logging.warning("The 'Next' button was not found or an error occurred when pressing it!")
            # Если кнопка "Далее" не найдена, выходим из цикла
            break

    # Завершаем сеанс браузера
    driver.quit()

if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(filename="image_download.log", level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")

    try:
        # Загрузка полноразмерных изображений для классов "leopard" и "tiger"
        download_images("tiger", num_images=5, full_size=True)
        download_images("leopard", num_images=5, full_size=True)

        # Загрузка миниатюр для классов "leopard" и "tiger"
        download_images("tiger", num_images=30, full_size=False)
        download_images("leopard", num_images=30, full_size=False)
    except Exception as e:
        logging.error(f"An error has occurred: {str(e)}")

