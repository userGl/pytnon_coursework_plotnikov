from fastapi import FastAPI, File, UploadFile, Body, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from typing import List
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
import pytest

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
    logger.info("Приложение запущено")
    yield
    logger.info("Приложение остановлено")

# 1. OCR endpoints
@app.get("/")                     # Главная страница (OCR)
async def base(request: Request):
    text = "Нет распознаного текста"    
    return templates.TemplateResponse(request, "ocr.html", {"text": text})

@app.post("/OCR/upload/")
async def upload_file(file: UploadFile, lang: str = Form(...)):
    """API endpoint для загрузки и OCR файла"""
    try:
        logger.info(f"Получен файл: {file.filename}, язык: {lang}")
        
        content = await file.read()
        current_datetime = datetime.now()
        date_time1 = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        temp_file_path = f"app/temp/{date_time1}_{file.filename}"
        
        with open(temp_file_path, "wb") as f:
            f.write(content)          
        
        ocr = Tesseract()
        result = ocr.ocr_recognize2(temp_file_path, lang)    
        
        if result["status"] == False:
            logger.warning(f"Ошибка распознавания файла {file.filename}: {result['text']}")
            os.remove(temp_file_path)
            # При ошибке просто возвращаем результат без сохранения в БД
            return {
                "status": result["status"],
                "text": result["text"]
            }
        else:
            logger.info(f"Успешное распознавание файла {file.filename}")
            repo_file_path = f"repository/files/{date_time1}_{file.filename}"
            shutil.move(temp_file_path, repo_file_path)
            # Сохраняем в БД только успешные результаты
            record_id = repository.add(
                file_name=repo_file_path,
                ocr_txt=result["text"],
                status=result["status"]
            )
            
            return {
                "status": result["status"],
                "text": result["text"],
                "id": record_id
            }
        
    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/OCR/get_languages/")   # Получение списка языков
async def get_languages():
    """Возвращает список доступных языков"""
    ocr = Tesseract()
    return ocr.get_languages()

# 2. Notifier endpoints
@app.post("/notifier/send_email/")  # Отправка на email
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
    except Exception as e:
        logger.error(f"Ошибка при отправке email {data['to_email']}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# 3. Records endpoints
@app.get("/records/")              # <-- Обратите внимание на слеш в конце
async def records_page(
    request: Request,
    keyword: Optional[str] = None,
    filename: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """HTML страница поиска записей"""
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

@app.get("/records/search")
async def search_records(
    keyword: Optional[str] = None,
    filename: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """API endpoint для поиска записей"""
    try:
        # Добавляем логирование для отладки
        logger.info(f"Поиск записей: keyword={keyword}, filename={filename}, date_from={date_from}, date_to={date_to}")
        
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
        
        # Логируем результаты
        logger.info(f"Найдено записей: {len(data)}")
        
        # Проверяем существование файлов
        for item in data:
            if item['file_name'].startswith('repository/files/'):
                item['file_exists'] = Path(item['file_name']).exists()

        return data
    except Exception as e:
        logger.error(f"Ошибка при поиске записей: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/records/delete")
async def delete_records(record_ids: List[int] = Body(..., embed=True)):
    """API endpoint для удаления записей"""
    try:
        logger.info(f"Запрос на удаление записей: {record_ids}")
        not_found = []
        
        for record_id in record_ids:
            if not repository.delete_by_id(record_id):
                not_found.append(record_id)
        
        if not_found:
            return JSONResponse(
                status_code=404,
                content={"error": f"Записи не найдены: {not_found}"}
            )
            
        logger.info(f"Успешно удалено записей: {len(record_ids)}")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Ошибка при удалении записей: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# 4. Admin endpoints
@app.get("/admin/")               # Панель администратора
async def admin_page(request: Request):    
    # Получаем настройки email из базы
    email_config = repository.get_email_settings()
    
    # Если есть настройки, инициализируем сервис уведомлений
    if email_config:
        config = EmailConfig(**email_config)
        notification_service.configure_email(config)
    
    return templates.TemplateResponse(
        request=request,
        name="admin.html", 
        context={
            "email_config": email_config
        }
    )

@app.get("/admin/logs")          # Получение логов
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

@app.get("/admin/run_test/{test_type}")  # Запуск тестов
async def run_test(test_type: str):
    """Запуск тестов через админ-панель"""
    try:
        # Определяем какие тесты запускать
        if test_type == "all":
            test_path = "tests"
        elif test_type == "ocr":
            test_path = "tests/test_ocr_server.py"
        elif test_type in ["endpoints", "repository"]:
            test_path = f"tests/test_{test_type}.py"
        else:
            return {"error": "Неизвестный тип тестов"}

        args = [test_path, "-v", "--tb=short"]
        
        # Перехватываем вывод pytest
        import io
        import sys
        output = io.StringIO()
        sys.stdout = output
        
        pytest.main(args)
        
        # Восстанавливаем stdout
        sys.stdout = sys.__stdout__
        
        return {"output": output.getvalue()}
        
    except Exception as e:
        logger.error(f"Ошибка при запуске тестов: {str(e)}")
        return {"error": str(e)}

@app.post("/admin/email_config")  # Настройка SMTP
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

# 5. About endpoint
@app.get("/about/")               # О проекте
async def about_page(request: Request):
    """Страница о проекте"""
    return templates.TemplateResponse(request, "about.html")

# Монтирование статических файлов
app.mount("/static/repository/files", StaticFiles(directory="repository/files"), name="repository_files")

#uvicorn app.main:app --reload
#python post_file_to_server.py