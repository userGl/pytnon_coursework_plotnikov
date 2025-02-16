from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_about_endpoint():
    """Тест страницы About"""
    response = client.get("/about/")
    assert response.status_code == 200

def test_admin_endpoint():
    """Тест страницы администратора"""
    response = client.get("/admin/")
    assert response.status_code == 200

def test_ocr_endpoint():
    """Тест страницы OCR"""
    response = client.get("/")  # Теперь OCR на главной странице
    assert response.status_code == 200

def test_get_records():
    """Тест endpoint получения записей"""
    # Проверяем получение всех записей (без параметров)
    response = client.get("/records/search")
    assert response.status_code == 200
    
    # Проверяем поиск с параметрами
    response = client.get("/records/search?keyword=test")
    assert response.status_code == 200 