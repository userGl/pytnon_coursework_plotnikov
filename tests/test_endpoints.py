from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Тест главной страницы"""
    response = client.get("/")
    assert response.status_code == 200

def test_admin_endpoint():
    """Тест страницы администратора"""
    response = client.get("/admin/")
    assert response.status_code == 200

def test_ocr_endpoint():
    """Тест страницы OCR"""
    response = client.get("/OCR/")
    assert response.status_code == 200

def test_get_records():
    """Тест endpoint получения записей"""
    response = client.get("/records/")
    assert response.status_code == 200
    assert isinstance(response.json(), list) 