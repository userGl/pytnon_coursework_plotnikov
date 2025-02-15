import pytest
from repository.repository import repository
from datetime import datetime

def test_add_record():
    """Тест добавления записи"""
    # Добавляем тестовую запись
    test_file = "test_file.txt"
    test_text = "Test text"
    
    assert repository.add(test_file, test_text, True)
    
    # Получаем все записи
    records = repository.get_all()
    
    # Проверяем что запись добавлена
    found = False
    record_id = None
    for record in records:
        if record["file_name"] == test_file and record["ocr_txt"] == test_text:
            found = True
            record_id = record["id"]
            break
    
    assert found, "Тестовая запись не найдена"
    
    # Очищаем тестовую запись
    if record_id:
        repository.delete_by_id(record_id)

def test_delete_record():
    """Тест удаления записи"""
    # Добавляем тестовую запись
    test_file = "test_delete.txt"
    test_text = "Delete test"
    
    repository.add(test_file, test_text, True)
    
    # Находим ID записи
    records = repository.get_all()
    record_id = None
    
    for record in records:
        if record["file_name"] == test_file:
            record_id = record["id"]
            break
    
    assert record_id is not None, "Тестовая запись не найдена"
    
    # Удаляем запись
    assert repository.delete_by_id(record_id), "Ошибка при удалении записи"
    
    # Проверяем что запись удалена
    records = repository.get_all()
    assert not any(r["file_name"] == test_file for r in records), "Запись не была удалена" 