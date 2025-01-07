import sqlite3
import datetime

conn = sqlite3.connect('exampe.db')

cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS товары (дата text, товар text, количество геal, цена геal)''')

cur.execute("INSERT INTO товары VALUES ('2021-11-12', 'журнал', 100, 200)")

# products = [('2021-11-13', 'Ручка', 100, 30),
#             ('2021-11-14', 'Тетрадь', 100, 50),
#             ('2021-11-15', 'Мел', 100, 15),
#             ]

# print(products)

# cur.execute("INSERT INTO товары VALUES (?, ?, ?, ?)", products)


cur.execute("SELECT * FROM товары")

for i in cur.fetchall():
    print(i)

conn.commit()

conn.close()
