import pytest
from fastapi.testclient import TestClient
import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Отслеживаем текущий файл тестов
current_test_file = None

@pytest.fixture
def client():
    """Фикстура для тестирования FastAPI endpoints"""
    return TestClient(app)

def pytest_runtest_protocol(item, nextitem):
    """Вывод заголовков перед каждой группой тестов"""
    global current_test_file
    
    if str(item.fspath) != current_test_file:
        if "test_endpoints.py" in str(item.fspath):
            print("\n\n=== Запуск тестов endpoints ===")
        elif "test_ocr_server.py" in str(item.fspath):
            print("\n\n=== Запуск тестов OCR ===")
        elif "test_repository.py" in str(item.fspath):
            print("\n\n=== Запуск тестов репозитория ===")
        current_test_file = str(item.fspath)

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Вывод результатов тестирования"""
    print("\n=== Результаты тестирования ===")
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    print(f"Всего тестов: {passed + failed}")
    print(f"Успешно: {passed}")
    print(f"Провалено: {failed}") 