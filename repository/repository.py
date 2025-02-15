# repository/ocr_repositoru.py

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, or_
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
from sqlalchemy.sql import text
from logger_config import logger

# Создаем базовый класс для моделей
Base = declarative_base()

class OcrData(Base):
    """Модель данных OCR"""
    __tablename__ = 'ocr_data'

    id = Column(Integer, primary_key=True)  # Автоинкремент по умолчанию
    date_time = Column(DateTime, default=datetime.now)
    file_name = Column(String)
    ocr_txt = Column(String)
    status = Column(String)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование записи в словарь"""
        return {
            'id': self.id,
            'date_time': self.date_time.strftime('%Y-%m-%d %H:%M:%S'),
            'file_name': self.file_name,
            'ocr_txt': self.ocr_txt,
            'status': self.status
        }

class EmailSettings(Base):
    """Модель для хранения настроек SMTP"""
    __tablename__ = 'email_settings'

    id = Column(Integer, primary_key=True)
    smtp_server = Column(String)
    smtp_port = Column(Integer)
    smtp_user = Column(String)
    smtp_password = Column(String)
    from_email = Column(String)

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
    def search_documents(self, keyword: Optional[str] = None, 
                        filename: Optional[str] = None,
                        date_from: Optional[datetime] = None,
                        date_to: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Поиск документов по различным критериям"""
        pass

    @abstractmethod
    def delete_by_filename(self, file_name: str) -> bool:
        """Удаляет записи по имени файла и соответствующий файл"""
        pass

    @abstractmethod
    def save_email_settings(self, config: dict) -> bool:
        """Сохраняет настройки email"""
        pass

    @abstractmethod
    def get_email_settings(self) -> Optional[dict]:
        """Получает настройки email"""
        pass

    @abstractmethod
    def delete_by_id(self, record_id: int):
        """Удаление записи по ID"""
        pass

    @abstractmethod
    def get_by_id(self, record_id: int) -> Optional[dict]:
        """Получение записи по ID"""
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
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def add(self, file_name: str, ocr_txt: str, status: bool) -> bool:
        try:
            with self._get_session() as session:
                ocr_txt = str(ocr_txt).strip() if ocr_txt else ""
                file_name = str(file_name).strip() if file_name else ""
                
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
        try:
            with self._get_session() as session:
                return [record.to_dict() 
                        for record in session.query(OcrData)
                        .order_by(OcrData.date_time.desc())  # Сортировка по убыванию даты
                        .all()]
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []

    def get_by_status(self, status: bool) -> List[Dict[str, Any]]:
        try:
            with self._get_session() as session:
                return [record.to_dict() 
                        for record in session.query(OcrData)
                        .filter(OcrData.status == str(status)).all()]
        except Exception as e:
            print(f"Ошибка при получении данных по статусу: {e}")
            return []

    def get_by_date(self, date: datetime) -> List[Dict[str, Any]]:
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

    def search_documents(self, keyword: Optional[str] = None, 
                        filename: Optional[str] = None,
                        date_from: Optional[datetime] = None,
                        date_to: Optional[datetime] = None) -> List[Dict[str, Any]]:
        try:
            with self._get_session() as session:
                query = session.query(OcrData)
                
                if keyword:
                    search_conditions = [
                        OcrData.ocr_txt.ilike(f'%{keyword.lower()}%'),
                        OcrData.ocr_txt.ilike(f'%{keyword.upper()}%'),
                        OcrData.ocr_txt.ilike(f'%{keyword.capitalize()}%')
                    ]
                    query = query.filter(or_(*search_conditions))
                
                if filename:
                    query = query.filter(OcrData.file_name.ilike(f'%{filename}%'))
                
                if date_from:
                    query = query.filter(OcrData.date_time >= date_from)
                
                if date_to:
                    query = query.filter(OcrData.date_time <= date_to)
                
                return [record.to_dict() 
                        for record in query
                        .order_by(OcrData.date_time.desc())  # Сортировка по убыванию даты
                        .all()]
        except Exception as e:
            print(f"Ошибка при поиске данных: {e}")
            return []

    def delete_by_filename(self, file_name: str) -> bool:
        """Удаляет записи по имени файла и соответствующий файл"""
        try:
            with self._get_session() as session:
                records = session.query(OcrData).filter(OcrData.file_name == file_name).all()
                for record in records:
                    # Если это распознанный файл, удаляем его из файловой системы
                    if record.file_name.startswith('repository/files/'):
                        file_path = Path(record.file_name)
                        if file_path.exists():
                            file_path.unlink()  # Удаляем файл
                    session.delete(record)  # Удаляем запись из БД
                return True
        except Exception as e:
            print(f"Ошибка при удалении данных: {e}")
            return False

    def save_email_settings(self, config: dict) -> bool:
        """Сохраняет настройки email"""
        try:
            with self._get_session() as session:
                # Удаляем старые настройки
                session.query(EmailSettings).delete()
                
                # Добавляем новые
                settings = EmailSettings(**config)
                session.add(settings)
                return True
        except Exception as e:
            print(f"Ошибка при сохранении настроек email: {e}")
            return False

    def get_email_settings(self) -> Optional[dict]:
        """Получает настройки email"""
        try:
            with self._get_session() as session:
                settings = session.query(EmailSettings).first()
                if settings:
                    return {
                        'smtp_server': settings.smtp_server,
                        'smtp_port': settings.smtp_port,
                        'smtp_user': settings.smtp_user,
                        'smtp_password': settings.smtp_password,
                        'from_email': settings.from_email
                    }
                return None
        except Exception as e:
            print(f"Ошибка при получении настроек email: {e}")
            return None

    def delete_by_id(self, record_id: int):
        """Удаление записи по ID"""
        try:
            with self._get_session() as session:
                # Получаем имя файла перед удалением
                record = session.query(OcrData).filter(OcrData.id == record_id).first()
                if record:
                    file_name = record.file_name
                    # Удаляем файл, если он существует и не является специальным маркером "--"
                    if file_name != "--" and file_name.startswith('repository/files/'):
                        file_path = Path(file_name)
                        if file_path.exists():
                            file_path.unlink()
                    session.delete(record)  # Удаляем запись из БД
                    return True
                return False
        except Exception as e:
            print(f"Ошибка при удалении записи {record_id}: {str(e)}")
            return False

    def get_by_id(self, record_id: int) -> Optional[dict]:
        """Получение записи по ID"""
        try:
            with self._get_session() as session:
                record = session.query(OcrData).filter(OcrData.id == record_id).first()
                return record.to_dict() if record else None
        except Exception as e:
            print(f"Ошибка при получении записи {record_id}: {str(e)}")
            return None

# Создаем единственный экземпляр репозитория
repository = SQLAlchemyRepository()