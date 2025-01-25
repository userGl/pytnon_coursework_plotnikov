from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

import PIL, os
import datetime

from app.tesseract import Tesseract
from repository.repository import repository

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
#def read_root():    
async def base(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})
    #return {"message": "Добро пожаловать в Tessaract-OCR !!!"}

@app.get("/admin/", response_class=HTMLResponse)
async def demo_data(request: Request):    
    data = repository.get_all()
    return templates.TemplateResponse("demo_data.html", {"request": request, "data": data})

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
    return templates.TemplateResponse("my_template.html", {"request": request, "text": text}) 



#uvicorn app.main:app --reload
#python post_file_to_server.py