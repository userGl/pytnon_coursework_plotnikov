from fastapi.testclient import TestClient
from app_practic import app

client = TestClient(app)

def test_create_task():
    response = client.post("/tasks", json={
        "id": 1,
        "title": "Сходить в магазин",
        "description": "Купить продукты",
        "completed": False
    })
    assert response.status_code == 200
    assert response.json() == {
        "message": "Задача добавлена!",
        "task": {
            "id": 1,
            "title": "Сходить в магазин",
            "description": "Купить продукты",
            "completed": False
        }
    }

def test_get_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()["tasks"]) > 0

def test_delete_task():
    response = client.delete("/tasks/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Задача удалена!"}

def test_search_task():
    # Создаем новую задачу для теста
    client.post("/tasks", json={
        "id": 2,
        "title": "Сходить в аптеку",
        "description": "Купить лекарства",
        "completed": False
    })
    
    # Ищем задачу по заголовку
    response = client.get("/tasks/search?title=аптеку")
    
    # Проверяем статус ответа
    assert response.status_code == 200
    
    # Проверяем, что результат содержит задачу с нужным заголовком
    tasks = response.json()["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Сходить в аптеку"

