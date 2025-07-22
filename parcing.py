from time import process_time
from playwright.sync_api import sync_playwright
import json, time, random, sqlite3
from datetime import datetime

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(
        "https://www.olx.ua/uk/nedvizhimost/kvartiry/prodazha-kvartir/kropivnitskiy/?currency=USD&search%5Bfilter_enum_number_of_rooms_string%5D%5B0%5D=odnokomnatnye&search%5Bfilter_float_price%3Afrom%5D=15000&search%5Bfilter_float_price%3Ato%5D=50000&search%5Bfilter_float_total_area%3Afrom%5D=20&search%5Bfilter_float_total_area%3Ato%5D=40&search%5Border%5D=created_at%3Adesc", timeout=60000)
    time.sleep(random.uniform(5, 8))
    data = []
    while True:
        page.wait_for_selector('[data-cy="l-card"]')

        # Получаем карточки и печатаем текст
        cards = page.locator('[data-cy="l-card"]')
        count = cards.count()
        for i in range(count):
            card = cards.nth(i)
            text = card.inner_text().splitlines()
            price = None
            area = None
            for b in text:
                if "$" in b:
                    price = b
                if "м²" in b:
                    area = b
            data.append({"price": price, "area": area})
        next_btn = page.locator('[data-testid="pagination-forward"]')
        if next_btn.count() > 0 and next_btn.is_visible():
            next_btn.click()
            time.sleep(random.uniform(5,7))
        else: break

new_data = []
for star in data:
    price_str = star["price"].replace("$", "").replace(" ", "")
    area_str = star["area"].replace("м²", "").replace(" ", "")
    price_str = int(price_str)
    area_str = float(area_str)
    new_data.append({"price": price_str, "area": area_str})

# Удаление повторений с одинаковыми ценами и квадратурой
unique_data = []
for item in new_data:
    if item not in unique_data:
        unique_data.append(item)
print(unique_data)

# Подключаемся к БД
conn = sqlite3.connect("data/flats.db")
cursor = conn.cursor()

# Создаём таблицу
cursor.execute("""
               CREATE TABLE IF NOT EXISTS flats
               (
                   id
                   INTEGER
                   PRIMARY
                   KEY
                   AUTOINCREMENT,
                   price
                   INTEGER,
                   area
                   REAL,
                   parsed_at
                   TEXT
               )
               """)

# Текущая дата и время
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Проверяем дату последней записи
cursor.execute("SELECT MAX(parsed_at) FROM flats")
last_date = cursor.fetchone()[0]

should_write = True
if last_date:
    last_date_obj = datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S")
    now_obj = datetime.now()
    days_diff = (now_obj - last_date_obj).days
    if days_diff < 7:
        print("⏳ Менее 7 дней с последней записи — данные не будут добавлены.")
        should_write = False

# Вставка данных, если прошло 7+ дней
if should_write:
    for item in unique_data:
        cursor.execute("INSERT INTO flats (price, area, parsed_at) VALUES (?, ?, ?)",
                       (item["price"], item["area"], now))
    print("✅ Данные добавлены в базу.")


# Заходим в БД чтобы отобразить разные данные что нам нужны

cursor.execute("SELECT price, area FROM flats")
rows = cursor.fetchall()

prices = []
areas = []
for price, area in rows:
    prices.append(price)
    areas.append(area)

average_price = round(sum(prices) / len(prices))
average_area = round(sum(areas) / len(areas))
print("Средняя стоимость и средняя площадь: ", average_price, average_area)


filtered_prices = []
for i in range(len(areas)):
    if 30 <= areas[i] <= 35:
        filtered_prices.append(prices[i])
sr_price_30_35 = round(sum(filtered_prices) / len(filtered_prices))
print("Средняя стоимость квартир от 30 до 35м: ", sr_price_30_35)

price_1m = round(sum(prices) / sum(areas))
print("Средняя цена за 1 м²:", price_1m)

conn.commit()
conn.close()
conn2 = sqlite3.connect("data/pokazateli.db")
cursor2 = conn2.cursor()

# Создаём таблицу
cursor2.execute("""
               CREATE TABLE IF NOT EXISTS pokazateli
               (
                   id
                       INTEGER
                       PRIMARY
                           KEY
                       AUTOINCREMENT,
                   avg_price
                       INTEGER,
                   avg_area
                       INTEGER,
                   avg_price_per_m2
                       INTEGER,
                   avg_30_35
                       INTEGER,
                   date
                       TEXT
                   
               )
               """)
cursor2.execute("""
               INSERT INTO pokazateli (avg_price, avg_area, avg_price_per_m2, avg_30_35, date)
               VALUES (?, ?, ?, ?, ?)
               """, (average_price, average_area, price_1m, sr_price_30_35, now))

conn2.commit()
conn2.close()