from fastapi import FastAPI, File, UploadFile
import tesseract

app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"message": "Добро пожаловать в FastAPI"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str = None):
#     return {"item_id": item_id, "q": q}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Загружает файл и возвращает информацию о нем."""
    content = await file.read()
    file_path = f"temp/uploaded_{file.filename}"
    with open(file_path, "wb") as f:
       f.write(content)
    text = tesseract.ocr_recognize(file_path, 'rus+eng')
    return {"filename": file.filename, "size": len(content), "text": text }


#uvicorn app:app --reload