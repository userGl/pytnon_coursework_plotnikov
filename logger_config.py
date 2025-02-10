from loguru import logger
import sys
from pathlib import Path
import os

# Получаем абсолютный путь к директории проекта
project_dir = Path(__file__).parent
log_dir = project_dir / "logs"

# Создаем директорию для логов если её нет
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Конфигурация логгера
logger.remove()  # Удаляем стандартный обработчик

# Путь к файлу логов (используем абсолютный путь)
log_file = str(log_dir / "ocr_app_{time:YYYY-MM-DD}.log")

# Добавляем вывод в файл
logger.add(
    log_file,
    rotation="00:00",  # Новый файл каждый день в полночь
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO",
    compression="zip",  # Сжимаем старые логи
    encoding="utf-8"
)

# Добавляем вывод в консоль
logger.add(
    sys.stderr,
    format="{time:HH:mm:ss} | {level} | {message}",
    level="INFO"
)

# Проверяем, что логгер работает
logger.info("Логгер инициализирован") 