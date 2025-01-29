from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

import PIL, os
import datetime
import subprocess

from app.tesseract import Tesseract
from repository.repository import repository

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def base(request: Request):
    return templates.TemplateResponse(request, "base.html")

@app.get("/admin/", response_class=HTMLResponse)
async def demo_data(request: Request):    
    data = repository.get_all()
    return templates.TemplateResponse(request, "demo_data.html", {"data": data})

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Загружает файл и возвращает информацию о нем."""
    content = await file.read()
    current_datetime = datetime.datetime.now()
    date_time1 = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    date_time2 = current_datetime.strftime("%d-%m-%Y %H:%M")    
    file_path = f"app/temp/{date_time1}_{file.filename}" 
    with open(file_path, "wb") as f:
       f.write(content)          
    ocr = Tesseract() #Класс Tessaract занимается распознаванием изображения. На вход путь к файлу, на выходе текст
    result = ocr.ocr_recognize2(file_path, 'rus+eng')    
    if result["status"] == False:
        os.remove(file_path) #Если формат файла не правильный удаляем из папки temp
        repository.add("--", result["text"], False)
    else:
        repository.add(file_path, result["text"], True)
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

#uvicorn app.main:app --reload
#python post_file_to_server.py