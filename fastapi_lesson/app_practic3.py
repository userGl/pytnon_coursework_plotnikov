from fastapi import FastAPI, Query, Path, Body, Form, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import httpx
from typing import Union, List, Dict
import os
import time

app = FastAPI()

# Модель данных для задач
class Task():
    id: int
    title: str # r = "4"; d = 4
    description: Optional[str] = None
    completed: bool = False

# Модель запроса, где поле 'data' может быть числом, строкой, списком или словарем
class DataRequest(BaseModel):
    data: Union[int, str, List[int], Dict[str, int]]  # Можно добавить другие типы по мере необходимости


# Локальное хранилище данных
tasks = []

# --- Маршруты ---

@app.get("/")
def read_root():
    """Маршрут для проверки работы приложения."""
    return {"message": "Добро пожаловать в API!"}


@app.get("/tasks/")
def get_all_tasks():
    """Возвращает все задачи."""
    return {"tasks": tasks}


@app.get("/tasks/{task_id}")
def get_task(task_id: int = Path(..., title="ID задачи", ge=1)):
    """Возвращает задачу по ID."""
    task = next((task for task in tasks if task.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task

@app.post("/check_data_type/")
def check_data_type(request: DataRequest):
    data = request.data  # Получаем данные из запроса
    data_type = type(data)  # Определяем тип данных

    # Создаем описание типа данных
    if isinstance(data, int):
        help_text = f"Введено число: {data}. Тип данных: целое число."
    elif isinstance(data, str):
        help_text = f"Введена строка: {data}. Тип данных: строка."
    elif isinstance(data, list):
        help_text = f"Введен список: {json.dumps(data)}. Тип данных: список целых чисел."
    elif isinstance(data, dict):
        help_text = f"Введен словарь: {json.dumps(data)}. Тип данных: словарь с ключами типа строки и значениями типа целое число."
    else:
        help_text = f"Неизвестный тип данных: {data_type}."

    # Возвращаем информацию о типе данных
    return {"data_type": str(data_type), "help_info": help_text}

@app.post("/tasks/")
def create_task(task: Task):
    """Создает новую задачу."""
    if any(t.id == task.id for t in tasks):
        raise HTTPException(status_code=400, detail="Задача с таким ID уже существует")
    tasks.append(task)
    return {"message": "Задача добавлена", "task": task}


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    """Обновляет задачу по ID."""
    index = next((i for i, t in enumerate(tasks) if t.id == task_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    tasks[index] = task
    return {"message": "Задача обновлена", "task": task}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    """Удаляет задачу по ID."""
    global tasks
    tasks = [task for task in tasks if task.id != task_id]
    return {"message": "Задача удалена"}


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Загружает файл и возвращает информацию о нем."""
    content = await file.read()
    file_path = f"uploaded_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    return {"filename": file.filename, "size": len(content)}


@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    """Авторизация через форму."""
    if username == "admin" and password == "admin":
        return {"message": "Добро пожаловать, администратор!"}
    else:
        raise HTTPException(status_code=401, detail="Неверные учетные данные")


@app.get("/search/")
def search_tasks(query: str = Query(..., min_length=3, max_length=50)):
    """Поиск задач по названию."""
    matching_tasks = [task for task in tasks if query.lower() in task.title.lower()]
    return {"tasks": matching_tasks}


@app.get("/download_csv/")
async def download_csv(file_url: str = Query(..., title="Ссылка на CSV файл")):
    """Скачивает CSV файл по ссылке."""
    file_url = file_url.strip()
    download_path = "downloaded_file.csv"

    # Скачиваем файл
    start_time = time.time()
    async with httpx.AsyncClient() as client:
        response = await client.get(file_url)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Не удалось скачать файл")

    with open(download_path, "wb") as f:
        f.write(response.content)
    end_time = time.time()

    file_size = os.path.getsize(download_path)
    return {
        "file_path": download_path,
        "file_size": file_size,
        "download_time": end_time - start_time,
    }
