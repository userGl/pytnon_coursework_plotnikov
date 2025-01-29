import pytest
from repository.repository import repository
from datetime import datetime

def test_add_and_get():
    """
    Тест добавления записи и её получения
    """
    # Добавляем тестовую запись
    test_file = "test_file.png"
    test_text = "Test text"
    test_status = True
    
    repository.add(test_file, test_text, test_status)
    
    # Получаем все записи
    records = repository.get_all()
    
    # Проверяем, что наша запись есть в списке
    found = False
    for record in records:
        if record["file_name"] == test_file and record["ocr_txt"] == test_text:
            found = True
            break
    
    assert found, "Тестовая запись не найдена в базе данных"
    
    # Очищаем тестовые данные
    repository.delete_by_filename(test_file)

def test_get_by_status():
    """
    Тест получения записей по статусу
    """
    # Добавляем тестовые записи с разными статусами
    repository.add("success.png", "Success text", True)
    repository.add("failure.png", "Failure text", False)
    
    # Получаем записи с успешным статусом
    success_records = repository.get_by_status(True)
    assert any(record["file_name"] == "success.png" for record in success_records)
    
    # Получаем записи с неуспешным статусом
    failure_records = repository.get_by_status(False)
    assert any(record["file_name"] == "failure.png" for record in failure_records)
    
    # Очищаем тестовые данные
    repository.delete_by_filename("success.png")
    repository.delete_by_filename("failure.png") 