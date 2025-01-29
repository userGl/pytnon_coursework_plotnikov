import pytest
import requests
from pathlib import Path
from repository.repository import repository

# Файлы отправляем берутся из path и отправляются на url
url = 'http://127.0.0.1:8000/upload/'
path = Path("tests/tests_data")

# Тестовые данные для проверки работы Tessaract
testfiles = ["test_wrong_type.txt", "test_no_letters.png", "test_text_ok_ru.png", "test_text_ok_en.png", "test_empy_pict.png"]
results_lst = [
    {"status": False, "text": "Ошибка: Неправильный формат файла"},
    {"status": False, "text": "Ошибка: Текст слишком короткий или не содержит букв"},
    {"status": True, "text": "Это тестовое сообщение на русском языке."},
    {"status": True, "text": "This is test message on English."},
    {"status": False, "text": "Ошибка: Текст слишком короткий или не содержит букв"}
]

def send_file(file_path: Path) -> dict:
    """Отправка файла на сервер OCR"""
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (file_path.name, file, 'multipart/form-data')}
            response = requests.post(url, files=files)
            return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Ошибка при отправке файла {file_path}: {str(e)}")
        return None

@pytest.fixture(scope="session", autouse=True)
def cleanup_after_tests():
    """Очистка тестовых данных после тестов"""
    yield
    # После выполнения всех тестов очищаем тестовые данные
    for test_file in testfiles:
        repository.delete_by_filename(test_file)

@pytest.mark.parametrize("test_file, expected_result", list(zip(testfiles, results_lst)))
def test_ocr(test_file, expected_result):
    """Тестирование OCR для различных типов файлов"""
    file_path = path / test_file
    
    # Проверяем существование файла
    assert file_path.exists(), f"Тестовый файл {test_file} не найден"
    
    # Отправляем файл и получаем результат
    result = send_file(file_path)
    
    # Проверяем ответ сервера
    assert result is not None, "Нет ответа от сервера"
    assert result["status"] == expected_result["status"], \
        f"Неверный статус для файла {test_file}"
    
    # Проверяем текст ответа
    if expected_result["status"]:
        # Для успешного распознавания сравниваем тексты
        assert result["text"].strip() == expected_result["text"].strip(), \
            f"Неверный текст для файла {test_file}"
    else:
        # Для ошибок проверяем, что текст ошибки содержит ожидаемое сообщение
        assert expected_result["text"].lower() in result["text"].lower(), \
            f"Неверное сообщение об ошибке для файла {test_file}" 
        
# pytest tests/test_ocr_server.py -v