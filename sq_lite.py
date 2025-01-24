import sqlite3
import datetime

db = 'repository/exampe.db'

class Sqlite:
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




# работа c sqlalcemy
# from sqlalchemy import create_engine, MetaData, Table

# # Создание подключения к базе данных
# engine = create_engine("sqlite:///european_database.sqlite")

# # Создание соединения с базой данных
# conn = engine.connect()

# # Инициализация объекта для метаданных
# metadata = MetaData()

# # Определение объекта таблицы с помощью метаданных
# division = Table('divisions', metadata, autoload_with=engine)  # объект таблицы

# # Печать метаданных таблицы 'divisions'
# print(repr(metadata.tables['divisions']))

# # Печать всех столбцов таблицы
# print(division.columns.keys())







# Так было сделано на лекции
# repository/movement_repository.py

# from abc import ABC, abstractmethod
# from datetime import datetime

# class Movement:
#     def __init__(self, timestamp: datetime, description: str):
#         self.timestamp = timestamp
#         self.description = description

# class MovementRepository(ABC):
#     @abstractmethod
#     def add_movement(self, movement: Movement):
#         pass

#     @abstractmethod
#     def get_movements(self):
#         pass

# class InMemoryMovementRepository(MovementRepository):
#     def __init__(self):
#         self.movements = []

#     def add_movement(self, movement: Movement):
#         self.movements.append(movement)

#     def get_movements(self):
#         return self.movements

# # Создание глобального репозитория
# global_repository = InMemoryMovementRepository()