from fastapi import FastAPI, File, UploadFile
import tesseract

import httpx, PIL, os

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request


app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Загружает файл и возвращает информацию о нем."""
    content = await file.read()
    file_path = f"temp/uploaded_{file.filename}"
    with open(file_path, "wb") as f:
       f.write(content)       
    try:
        text = tesseract.ocr_recognize(file_path, 'rus+eng')
    except PIL.UnidentifiedImageError as e:        
        print(f"Ошибка {e}")
        err = str(e)
        os.remove(file_path) #Если формат файла не правильный (не поддержвается PIL), удаляем 
        return {"text":err}
    else:
        return {"filename": file.filename, "size": len(content), "text": text }

# Моя статическая HTML-страница
@app.get("/my-page", response_class=HTMLResponse)
async def static_page(request: Request):
    text="Привет мир!!!"    
    return templates.TemplateResponse("my_template.html", {"request": request, "text": text}) 

# @app.get("/")
# def read_root():
#     return {"message": "Добро пожаловать в FastAPI"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str = None):
#     return {"item_id": item_id, "q": q}


# # Статическая HTML-страница
# @app.get("/static-page", response_class=HTMLResponse)
# async def static_page(request: Request):
#     text="Привет мир"    
#     return templates.TemplateResponse("static_page.html", {"request": request, "text": text}, )

# # Отображение данных в таблице
# @app.get("/demo-data", response_class=HTMLResponse)
# async def demo_data(request: Request):
#     data = [
#         {"name": "John", "age": 30},
#         {"name": "Jane", "age": 25},
#         {"name": "Alice", "age": 35}
#     ]
#     return templates.TemplateResponse("demo_data.html", {"request": request, "data": data})


#uvicorn app:app --reload
#python post_file_to_server.py