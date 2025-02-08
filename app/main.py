from fastapi import FastAPI, File, UploadFile, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from typing import List
from fastapi.staticfiles import StaticFiles
from pathlib import Path

import PIL, os
from datetime import datetime
import subprocess
from typing import Optional
import shutil

from app.tesseract import Tesseract
from repository.repository import repository
from app.notification_service import notification_service, EmailConfig
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Создаем папку для файлов, если её нет
REPOSITORY_FILES_DIR = Path("repository/files")
REPOSITORY_FILES_DIR.mkdir(parents=True, exist_ok=True)

# Монтируем директорию temp как статическую
app.mount("/static/app/temp", StaticFiles(directory="app/temp"), name="temp")

# Создаем пул потоков для асинхронных задач
executor = ThreadPoolExecutor()

@app.get("/", response_class=HTMLResponse)
async def base(request: Request):
    return templates.TemplateResponse(request, "base.html")

@app.get("/admin/", response_class=HTMLResponse)
async def admin_page(request: Request):    
    # Получаем настройки email из базы
    email_config = repository.get_email_settings()
    
    # Если есть настройки, инициализируем сервис уведомлений
    if email_config:
        config = EmailConfig(**email_config)
        notification_service.configure_email(config)
    
    return templates.TemplateResponse(
        "admin.html", 
        {
            "request": request,
            "email_config": email_config
        }
    )

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Загружает файл и возвращает информацию о нем."""
    content = await file.read()
    current_datetime = datetime.now()
    date_time1 = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    date_time2 = current_datetime.strftime("%d-%m-%Y %H:%M")    
    temp_file_path = f"app/temp/{date_time1}_{file.filename}"
    
    # Сначала сохраняем во временную папку
    with open(temp_file_path, "wb") as f:
        f.write(content)          
    
    ocr = Tesseract()
    result = ocr.ocr_recognize2(temp_file_path, 'rus+eng')    
    
    if result["status"] == False:
        # Если файл не распознан - удаляем его и записываем ошибку в БД
        os.remove(temp_file_path)
        repository.add("--", result["text"], False)
    else:
        # Если файл успешно распознан - перемещаем его в репозиторий
        repo_file_path = f"repository/files/{date_time1}_{file.filename}"
        shutil.move(temp_file_path, repo_file_path)
        repository.add(repo_file_path, result["text"], True)
    
    return result

# Cтатическая HTML-страница для распознавания текста
@app.get("/OCR/", response_class=HTMLResponse)
async def static_page(request: Request):
    text="Нет распознаного текста"    
    return templates.TemplateResponse(request, "my_template.html", {"text": text}) 

@app.get("/records/")
async def get_records():
    return repository.get_all()

@app.get("/tests/", response_class=HTMLResponse)
async def test_page(request: Request):
    return templates.TemplateResponse(request, "tests.html")

@app.get("/run_test/{test_type}")
async def run_test(test_type: str):
    cmd = {
        "all": ["pytest", "tests", "-v"],
        "endpoints": ["pytest", "tests/test_endpoints.py", "-v"],
        "repository": ["pytest", "tests/test_repository.py", "-v"],
        "ocr": ["pytest", "tests/test_ocr_server.py", "-v"]
    }.get(test_type)
    
    if not cmd:
        return JSONResponse(content={"error": "Неизвестный тип теста"})

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return JSONResponse(content={"output": result.stdout + (result.stderr or '')})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@app.get("/search/", response_class=HTMLResponse)
async def search_page(request: Request,
                     keyword: Optional[str] = None,
                     filename: Optional[str] = None,
                     date_from: Optional[str] = None,
                     date_to: Optional[str] = None):
    
    # Преобразуем строковые даты в datetime объекты
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    # Если есть параметры поиска, выполняем поиск
    if any([keyword, filename, date_from, date_to]):
        data = repository.search_documents(
            keyword=keyword,
            filename=filename,
            date_from=date_from_obj,
            date_to=date_to_obj
        )
    else:
        # Если параметров нет - возвращаем все записи
        data = repository.get_all()
    
    # Проверяем существование файлов
    for item in data:
        if item['file_name'].startswith('repository/files/'):
            item['file_exists'] = Path(item['file_name']).exists()
    
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "data": data,
            "keyword": keyword,
            "filename": filename,
            "date_from": date_from,
            "date_to": date_to
        }
    )

@app.post("/delete_records")
async def delete_records(filenames: List[str] = Body(..., embed=True)):
    """Удаляет выбранные записи из базы данных"""
    try:
        for filename in filenames:
            repository.delete_by_filename(filename)
        return {"status": "success"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# Обновляем монтирование статических файлов
app.mount("/static/repository/files", StaticFiles(directory="repository/files"), name="repository_files")

@app.post("/admin/email_config")
async def save_email_config(config: EmailConfig):
    """Сохраняет настройки SMTP"""
    try:
        if repository.save_email_settings(config.dict()):
            notification_service.configure_email(config)
            return {"status": "success"}
        return JSONResponse(
            status_code=500,
            content={"error": "Ошибка при сохранении в базу данных"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/send_email/")
async def send_email(data: dict):
    """Отправляет распознанный текст через уведомления"""
    if not notification_service.get_email_config():
        return JSONResponse(
            status_code=500,
            content={"error": "Email не настроен"}
        )

    try:
        success = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                executor,
                notification_service.notify_all,
                data["to_email"],
                "Результат распознавания текста",
                data["text"]
            ),
            timeout=60.0
        )

        if success:
            return {"status": "success"}
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Ошибка при отправке уведомления"}
            )
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=500,
            content={"error": "Превышено время ожидания отправки (1 минута)"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

#uvicorn app.main:app --reload
#python post_file_to_server.py