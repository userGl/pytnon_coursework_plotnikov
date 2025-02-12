from fastapi import FastAPI, File, UploadFile, Body, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from typing import List
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager

import PIL, os
from datetime import datetime
import subprocess
from typing import Optional
import shutil

from app.tesseract import Tesseract
from repository.repository import repository
from notifier.notification_service import notification_service, EmailConfig
import asyncio
from concurrent.futures import ThreadPoolExecutor
from logger_config import logger

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Создаем папку для файлов, если её нет
REPOSITORY_FILES_DIR = Path("repository/files")
REPOSITORY_FILES_DIR.mkdir(parents=True, exist_ok=True)

# Монтируем директорию temp как статическую
app.mount("/static/app/temp", StaticFiles(directory="app/temp"), name="temp")

# Создаем пул потоков для асинхронных задач
executor = ThreadPoolExecutor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Обработчик событий жизненного цикла приложения"""
    # Код выполняется при запуске
    logger.info("Приложение запущено")
    yield
    # Код выполняется при остановке
    logger.info("Приложение остановлено")

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
        request=request,  # Первым параметром передаем request
        name="admin.html", 
        context={
            "email_config": email_config
        }
    )

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), lang: str = Form(...)):
    """Загружает файл и возвращает информацию о нем."""
    logger.info(f"Получен файл: {file.filename}, язык: {lang}")
    
    content = await file.read()
    current_datetime = datetime.now()
    date_time1 = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    temp_file_path = f"app/temp/{date_time1}_{file.filename}"
    
    try:
        # Сначала сохраняем во временную папку
        with open(temp_file_path, "wb") as f:
            f.write(content)          
        
        ocr = Tesseract()
        result = ocr.ocr_recognize2(temp_file_path, lang)    
        
        if result["status"] == False:
            # Если распознавание не удалось - просто логируем ошибку
            logger.warning(f"Ошибка распознавания файла {file.filename}: {result['text']}")
            os.remove(temp_file_path)
        else:
            # Только успешные результаты сохраняем в БД
            logger.info(f"Успешное распознавание файла {file.filename}")
            repo_file_path = f"repository/files/{date_time1}_{file.filename}"
            shutil.move(temp_file_path, repo_file_path)
            repository.add(repo_file_path, result["text"], True)
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при обработке файла {file.filename}: {str(e)}")
        raise

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
async def delete_records(record_ids: List[int] = Body(..., embed=True)):
    """Удаляет выбранные записи из базы данных"""
    try:
        logger.info(f"Запрос на удаление записей: {record_ids}")
        for record_id in record_ids:
            repository.delete_by_id(record_id)
        logger.info(f"Успешно удалено записей: {len(record_ids)}")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Ошибка при удалении записей: {str(e)}")
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
        logger.info("Обновление настроек SMTP")
        if repository.save_email_settings(config.dict()):
            notification_service.configure_email(config)
            logger.info("Настройки SMTP успешно обновлены")
            return {"status": "success"}
        logger.error("Ошибка сохранения настроек SMTP в БД")
        return JSONResponse(
            status_code=500,
            content={"error": "Ошибка при сохранении в базу данных"}
        )
    except Exception as e:
        logger.error(f"Ошибка при сохранении настроек SMTP: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/send_email/")
async def send_email(data: dict):
    """Отправляет распознанный текст через уведомления"""
    logger.info(f"Запрос на отправку email для: {data['to_email']}")
    
    # Загружаем актуальную конфигурацию перед отправкой
    email_config = repository.get_email_settings()
    if email_config:
        config = EmailConfig(**email_config)
        notification_service.configure_email(config)

    if not notification_service.get_email_config():
        logger.error("Попытка отправки email без настроек SMTP")
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
            logger.info(f"Email успешно отправлен: {data['to_email']}")
            return {"status": "success"}
        else:
            logger.error(f"Ошибка при отправке email: {data['to_email']}")
            return JSONResponse(
                status_code=500,
                content={"error": "Ошибка при отправке уведомления"}
            )
    except asyncio.TimeoutError:
        logger.error(f"Таймаут при отправке email: {data['to_email']}")
        return JSONResponse(
            status_code=500,
            content={"error": "Превышено время ожидания отправки (1 минута)"}
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке email {data['to_email']}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/get_languages/")
async def get_languages():
    """Возвращает список доступных языков"""
    ocr = Tesseract()
    return ocr.get_languages()

@app.get("/admin/logs")
async def get_logs(lines: int = 100):
    """Возвращает последние строки лога"""
    try:
        log_dir = Path("logs")
        if not log_dir.exists():
            return {"logs": "Директория логов не найдена"}
            
        # Получаем самый свежий файл логов
        log_files = sorted(log_dir.glob("ocr_app_*.log"), reverse=True)
        if not log_files:
            return {"logs": "Файлы логов не найдены"}
            
        latest_log = log_files[0]
        
        # Читаем последние строки
        with open(latest_log, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return {"logs": "".join(all_lines[-lines:])}
            
    except Exception as e:
        logger.error(f"Ошибка при чтении логов: {str(e)}")
        return {"logs": f"Ошибка при чтении логов: {str(e)}"}

#uvicorn app.main:app --reload
#python post_file_to_server.py