import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os

# Настройки для Chrome WebDriver
options = Options()
options.add_argument("--no-sandbox")  # Устраняет проблемы с доступом к системе
options.add_argument("--disable-dev-shm-usage")  # Для избежания сбоев из-за недостатка ресурсов

driver = webdriver.Chrome(options=options)

url = 'https://www.divan.ru/category/svet'

try:
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'LlPhw'))  # Ждем загрузки карточек товаров
    )

    all_light = driver.find_elements(By.CLASS_NAME, 'LlPhw')
    print(f"Найдено товаров: {len(all_light)}")

    light_pars = []

    for light in all_light:
        try:
            # Извлечение наименования товара
            name = light.find_element(By.CLASS_NAME, 'ProductName').text
            print(f"Наименование: {name}")

            # Извлечение цен
            prices = light.find_elements(By.CLASS_NAME, 'ui-LD-ZU')
            price = prices[0].text.replace(' руб.', '').strip() if prices else "Цена отсутствует"
            print(f"Цена: {price}")

            # Попытка получить старую цену
            old_price = prices[1].text.replace(' руб.', '').strip() if len(prices) > 1 else "Скидка не применялась"
            print(f"Старая цена: {old_price}")

            # Извлечение ссылки
            link = light.find_element(By.TAG_NAME, 'a').get_attribute('href')
            print(f"Ссылка: {link}")

            # Добавление данных в список
            light_pars.append([name, price, old_price, link])

        except Exception as e:
            print(f"Ошибка при парсинге товара: {e}")
            continue

finally:
    driver.quit()

# Сохранение данных в CSV
output_dir = os.getcwd()  # Текущая рабочая директория
output_file = os.path.join(output_dir, 'lights.csv')  # Полный путь к файлу

try:
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Наименование", "Цена", "Цена без скидки", "Ссылка на товар"])
        writer.writerows(light_pars)
    print(f"Данные успешно сохранены в файл: {output_file}")
except Exception as e:
    print(f"Ошибка при записи в файл: {e}")
