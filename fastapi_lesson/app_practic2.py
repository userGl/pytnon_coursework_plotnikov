import os
import time
from urllib.parse import unquote
from fastapi import FastAPI, Form, File, UploadFile, Request, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import random
import string
import httpx

app = FastAPI()

# --- Middleware ---
class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Действия перед обработкой запроса
        response = await call_next(request)
        # Добавление заголовка X-Request-ID
        request_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        response.headers["X-Request-ID"] = request_id
        return response

app.add_middleware(CustomMiddleware)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешены запросы с любого источника
    allow_credentials=True,
    allow_methods=["*"],  # Разрешены все методы (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Разрешены все заголовки
)

# --- Модель данных ---
class Task(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False

# Хранилище для задач
tasks = []

# --- Маршруты ---

@app.post("/tasks")
async def create_task(task: Task):
    tasks.append(task)
    return {"message": "Задача добавлена!", "task": task}

@app.get("/tasks")
async def get_tasks():
    return {"tasks": tasks}

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    global tasks
    tasks = [task for task in tasks if task.id != task_id]
    return {"message": "Задача удалена!"}

@app.get("/tasks/search")
async def search_tasks(title: str, limit: int = 10):
    matching_tasks = [task for task in tasks if title.lower() in task.title.lower()]
    return {"tasks": matching_tasks[:limit]}

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "1234":
        return {"message": "Добро пожаловать, администратор!"}
    raise HTTPException(status_code=401, detail="Неверные учетные данные")

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()  # Считываем содержимое файла
    return {"filename": file.filename, "size": len(content)}


@app.get("/download_csv/")
async def download_csv(file_url: str):
    # Декодируем URL, если он был закодирован
    file_url = unquote(file_url)
    
    # Путь для сохранения файла
    download_path = "downloaded_file.csv" 

    # Запускаем асинхронный запрос для загрузки файла
    start_time = time.time()  # Засекаем время начала загрузки
    async with httpx.AsyncClient() as client:
        response = await client.get(file_url)

    # Проверяем, что запрос прошел успешно
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error downloading the file")

    # Сохраняем файл на диск
    with open(download_path, "wb") as f:
        f.write(response.content)

    # Засекаем время завершения загрузки
    end_time = time.time()

    # Получаем размер файла в байтах
    file_size = os.path.getsize(download_path)

    # Время загрузки
    download_time = end_time - start_time

    return JSONResponse(content={
        "file_path": download_path,
        "file_size": file_size,
        "download_time": download_time
    })
