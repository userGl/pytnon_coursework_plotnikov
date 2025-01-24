from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Создаем базовый класс для моделей
Base = declarative_base()

# Определение модели OcrData
class OcrData(Base):
    __tablename__ = 'ocr_data'

    id = Column(Integer, primary_key=True)
    date_time = Column(DateTime, default=datetime.now)
    file_name = Column(String)
    ocr_txt = Column(String)
    status = Column(String)

    def __repr__(self):
        return f"<OcrData (file_name='{self.file_name}', date_time={self.date_time})>"

# Создание двигателя подключения к базе данных SQLite 
engine = create_engine('sqlite:///repository/exampe.db', echo=False)

# Создание всех таблиц
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()

def add_ocr_data(file_name: str, ocr_txt: str, status: bool):
    """Добавление данных OCR в базу."""
    new_ocr_data = OcrData(
        file_name=file_name,
        ocr_txt=ocr_txt,
        status=status
    )
    session.add(new_ocr_data)
    session.commit()
    return True

def get_all_ocr_data():
    """Получение всех данных OCR из базы."""
    ocr_records = session.query(OcrData).all()
    result = []
    for record in ocr_records:
        result.append({
            'date_time': record.date_time.strftime('%Y-%m-%d %H:%M:%S'),
            'file_name': record.file_name,
            'ocr_txt': record.ocr_txt,
            'status' : record.status
        })
    return result

