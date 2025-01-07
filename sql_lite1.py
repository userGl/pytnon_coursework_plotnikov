import sqlite3 as sl

con = sl.connect('my-test.db')

with con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS OCR_DATA (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            date_time TEXT,
            filename TEXT,
            text TEXT
        );
    """)

#    sql = 'INSERT INTO OCR_DATA (id, date_time, filename, text) values(?, ?, ?, ?)'
# data = [
#     (1, 'Alice', 21),
#     (2, 'Bob', 22),
#     (3, 'Chris', 23)
# ]

# with con:
#     con.executemany(sql, data)

# with con:
#     data = con.execute("SELECT * FROM USER WHERE age <= 22")
#     for row in data:
#         print(row)