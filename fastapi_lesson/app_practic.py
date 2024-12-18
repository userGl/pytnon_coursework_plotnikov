"""
Проект: To-Do List
Создадим простое приложение для управления списком задач.
"""

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

# Модель данных задачи
class Task(BaseModel):
    id:  int
    title: str
    description: str
    coompleted: bool = False

# Хранилище данных
tasks = []

@app.post("/tasks")
def create_task(task: Task):
    tasks.append(task)
    return {"message": "Добавлена новая задача!", "task": task}

@app.get("/tasks")
def get_tasks():
    return {"tasks": tasks}

@app.get("/task/search")
def search_task(title: str):
    matching_tasks = [tasks for task in tasks if title.lower() in tasks.title.lower()]
    return {"tasks": matching_tasks}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks
    tasks = [task for task in tasks if task.id != task_id]
    return {"message": "Задача удалена!"}


# uvicorn app_practic:app












































"""
Чтоб взаимодействовать с приложением через PowerShell:  
------------------------------------------------------------------------------------------------------
GET-запрос:

Invoke-WebRequest -Uri "http://127.0.0.1:8000/tasks" -Method GET

------------------------------------------------------------------------------------------------------
POST-запрос:

Invoke-WebRequest -Uri "http://127.0.0.1:8000/tasks" '
-Method POST '
-Headers @{ "Content-Type" = "application/json" }'
-Body '{"id": 1, "title": "Сходить в магазин", "description": "Купить продукты", "completed": false}'
------------------------------------------------------------------------------------------------------
DELETE-запрос:

Invoke-WebRequest -Uri "http://127.0.0.1:8000/tasks/1" -Method DELETE

------------------------------------------------------------------------------------------------------
"""
