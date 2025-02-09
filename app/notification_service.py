from abc import ABC, abstractmethod
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pydantic import BaseModel
from typing import Optional, List
import logging
import os

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailConfig(BaseModel):
    """Модель для хранения настроек SMTP"""
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    from_email: str

class NotificationObserver(ABC):
    """Абстрактный класс наблюдателя для отправки уведомлений"""
    @abstractmethod
    def notify(self, recipient: str, subject: str, message: str) -> bool:
        pass

class EmailNotifier(NotificationObserver):
    """Отправка уведомлений через email"""
    def __init__(self, config: EmailConfig):
        self.config = config
        logger.info(f"EmailNotifier инициализирован с сервером {config.smtp_server}:{config.smtp_port}")

    def notify(self, recipient: str, subject: str, message: str) -> bool:
        try:
            logger.info(f"Начинаем отправку email для {recipient}")
            
            # Создаем временный файл
            temp_file = "temp_ocr.txt"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(message)
            
            # Создаем составное сообщение
            msg = MIMEMultipart()
            msg['From'] = self.config.from_email
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Добавляем текст в тело письма
            msg.attach(MIMEText("Результат распознавания во вложении"))
            
            # Добавляем файл как вложение
            with open(temp_file, "rb") as f:
                part = MIMEApplication(f.read(), Name="recognized_text.txt")
                part['Content-Disposition'] = 'attachment; filename="recognized_text.txt"'
                msg.attach(part)

            logger.info(f"Подключаемся к SMTP серверу {self.config.smtp_server}:{self.config.smtp_port}")
            with smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port) as server:
                logger.info(f"Авторизуемся с пользователем {self.config.smtp_user}")
                server.login(self.config.smtp_user, self.config.smtp_password)
                
                logger.info("Отправляем сообщение")
                server.send_message(msg)
                
                logger.info("Сообщение успешно отправлено")
                
            # Удаляем временный файл    
            os.remove(temp_file)
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки email: {str(e)}")
            return False

class NotificationService:
    """Сервис уведомлений"""
    def __init__(self):
        self._observers: List[NotificationObserver] = []
        self._email_config: Optional[EmailConfig] = None

    def configure_email(self, config: EmailConfig):
        """Настройка email уведомлений"""
        self._email_config = config
        self._observers = [obs for obs in self._observers if not isinstance(obs, EmailNotifier)]
        self.add_observer(EmailNotifier(config))

    def add_observer(self, observer: NotificationObserver):
        """Добавление наблюдателя"""
        if observer not in self._observers:
            self._observers.append(observer)

    def notify_all(self, recipient: str, subject: str, message: str) -> bool:
        """Отправка уведомления через всех наблюдателей"""
        success = True
        for observer in self._observers:
            if not observer.notify(recipient, subject, message):
                success = False
        return success

    def get_email_config(self) -> Optional[EmailConfig]:
        """Получение текущих настроек email"""
        return self._email_config

# Глобальный экземпляр сервиса уведомлений
notification_service = NotificationService() 