import sqlite3
import datetime

now = datetime.datetime.now(datetime.timezone.utc).astimezone()
time_format = "%Y-%m-%d_%H-%M"
time_label = f"{now:{time_format}}"


conn = sqlite3.connect('exampe.db')

cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS ocr_data (дата_время text, имя_файла text, распознано text)''')

cur.execute("INSERT INTO ocr_data (time_lable, 'test', 'привет')")

# products = [('2021-11-13', 'Ручка', 100, 30),
#             ('2021-11-14', 'Тетрадь', 100, 50),
#             ('2021-11-15', 'Мел', 100, 15),
#             ]

# print(products)

# cur.execute("INSERT INTO товары VALUES (?, ?, ?, ?)", products)


cur.execute("SELECT * FROM ocr_data")

for i in cur.fetchall():
    print(i)

conn.commit()

conn.close()
