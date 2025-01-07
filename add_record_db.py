import sqlite3 as sl
import datetime

con = sl.connect('my-test.db')

now = datetime.datetime.now(datetime.timezone.utc).astimezone()
time_format = "%Y-%m-%d_%H-%M"
time_label = f"{now:{time_format}}"

sql = 'INSERT INTO OCR_DATA (date_time, text) values(?, ?)'
data = [
    (time_label, 'test')
]