import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import time

# Настройки для Chrome WebDriver
options = Options()
options.add_argument("--no-sandbox")  # Устраняет проблемы с доступом к системе
options.add_argument("--disable-dev-shm-usage")  # Для избежания сбоев из-за недостатка ресурсов
options.add_argument("--headless")  # Запуск браузера в фоновом режиме
options.add_argument("--disable-gpu")  # Отключение GPU для повышения совместимости

# Инициализация драйвера
driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(60)

base_url = 'https://www.divan.ru/tyumen/category/nastolnye-lampy/page-{a}'

light_pars = []

try:
    page = 1  # Номер начальной страницы

    while True:
        url = base_url.format(a=page)
        print(f"Открытие страницы: {url}")

        try:
            driver.get(url)
            time.sleep(3)  # Небольшая пауза для корректной загрузки страницы
        except Exception as e:
            print(f"Ошибка при загрузке страницы {url}: {e}")
            break

        # Ожидание загрузки товаров на странице
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'LlPhw'))
            )
        except Exception:
            print("Товары не найдены на странице, возможно, это конец списка.")
            break

        all_light = driver.find_elements(By.CLASS_NAME, 'LlPhw')
        print(f"Найдено товаров на странице {page}: {len(all_light)}")

        if not all_light:
            print("Товары отсутствуют, завершаем парсинг.")
            break

        for light in all_light:
            try:
                # Извлечение наименования товара
                name = light.find_element(By.CLASS_NAME, 'ProductName').text if light.find_elements(By.CLASS_NAME, 'ProductName') else "Наименование отсутствует"

                # Извлечение цен
                prices = light.find_elements(By.CLASS_NAME, 'ui-LD-ZU')
                price = prices[0].text.replace(' руб.', '').strip() if prices else "Цена отсутствует"
                old_price = prices[1].text.replace(' руб.', '').strip() if len(prices) > 1 else "Скидка не применялась"

                # Извлечение ссылки
                link = light.find_element(By.TAG_NAME, 'a').get_attribute('href') if light.find_elements(By.TAG_NAME, 'a') else "Ссылка отсутствует"

                # Добавление данных в список
                light_pars.append([name, price, old_price, link])

            except Exception as e:
                print(f"Ошибка при парсинге товара: {e}")
                continue

        page += 1  # Переход на следующую страницу

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
