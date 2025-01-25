# repository/ocr_repositoru.py

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager

# Создаем базовый класс для моделей
Base = declarative_base()

class OcrData(Base):
    """Модель данных OCR"""
    __tablename__ = 'ocr_data'

    id = Column(Integer, primary_key=True)
    date_time = Column(DateTime, default=datetime.now)
    file_name = Column(String)
    ocr_txt = Column(String)
    status = Column(String)

    def __repr__(self):
        return f"<OcrData (file_name='{self.file_name}', date_time={self.date_time})>"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование записи в словарь"""
        return {
            'date_time': self.date_time.strftime('%Y-%m-%d %H:%M:%S'),
            'file_name': self.file_name,
            'ocr_txt': self.ocr_txt,
            'status': self.status
        }

class Repository(ABC):
    """Абстрактный базовый класс репозитория"""
    
    @abstractmethod
    def add(self, file_name: str, ocr_txt: str, status: bool) -> bool:
        """Добавить новую запись в репозиторий"""
        pass

    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        """Получить все записи из репозитория"""
        pass

    @abstractmethod
    def get_by_status(self, status: bool) -> List[Dict[str, Any]]:
        """Получить записи по статусу"""
        pass

    @abstractmethod
    def get_by_date(self, date: datetime) -> List[Dict[str, Any]]:
        """Получить записи по дате"""
        pass

    @abstractmethod
    def search_by_text(self, query: str) -> List[Dict[str, Any]]:
        pass

class SQLAlchemyRepository(Repository):
    """Реализация репозитория с использованием SQLAlchemy"""

    def __init__(self, db_url: str = 'sqlite:///repository/ocr_database.db'):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    @contextmanager
    def _get_session(self):
        """Контекстный менеджер для сессии базы данных"""
        session = self.Session() # Создание сессии
        try:
            yield session
            session.commit() # Коммит изменений при успехе
        except Exception as e:
            session.rollback() #О тмена изменений при ошибке
            raise e
        finally:
            session.close()

    def add(self, file_name: str, ocr_txt: str, status: bool) -> bool:
        """Добавить новую запись OCR в базу данных"""
        try:
            with self._get_session() as session:
                new_ocr_data = OcrData(
                    file_name=file_name,
                    ocr_txt=ocr_txt,
                    status=str(status)
                )
                session.add(new_ocr_data)
            return True
        except Exception as e:
            print(f"Ошибка при добавлении данных: {e}")
            return False

    def get_all(self) -> List[Dict[str, Any]]:
        """Получить все записи OCR из базы данных"""
        try:
            with self._get_session() as session:
                return [record.to_dict() for record in session.query(OcrData).all()]
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []

    def get_by_status(self, status: bool) -> List[Dict[str, Any]]:
        """Получить записи по статусу"""
        try:
            with self._get_session() as session:
                return [record.to_dict() 
                        for record in session.query(OcrData)
                        .filter(OcrData.status == str(status)).all()]
        except Exception as e:
            print(f"Ошибка при получении данных по статусу: {e}")
            return []

    def get_by_date(self, date: datetime) -> List[Dict[str, Any]]:
        """Получить записи по дате"""
        try:
            with self._get_session() as session:
                return [record.to_dict() 
                        for record in session.query(OcrData)
                        .filter(OcrData.date_time >= date.replace(hour=0, minute=0, second=0),
                               OcrData.date_time < date.replace(hour=23, minute=59, second=59))
                        .all()]
        except Exception as e:
            print(f"Ошибка при получении данных по дате: {e}")
            return []

    def search_by_text(self, query: str) -> List[Dict[str, Any]]:
        pass

# Создаем единственный экземпляр репозитория
repository = SQLAlchemyRepository()