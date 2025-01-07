import sqlite3
import datetime

db = 'exampe.db'

def sql_insert(data):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS ocr_data (date_time text, file_name text, ocr_txt text)''')
    cur.execute('''INSERT INTO ocr_data (date_time, file_name, ocr_txt) VALUES (?, ?, ?)''', data )
    conn.commit()
    conn.close()
    return True

def sql_read_all():
    conn = sqlite3.connect(db)
    cur = conn.cursor()    
    cur.execute("SELECT * FROM ocr_data")
    desc = cur.description
    column_names = [col[0] for col in desc]
    data = [dict(zip(column_names, row))  
        for row in cur.fetchall()]    
    conn.close()
    return data

if __name__ == "__main__":
    data = (f"{get_date_time()}", "test.txt", "test")
    sql_insert(data)
    sql_read_all()



