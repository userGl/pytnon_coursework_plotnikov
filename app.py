from fastapi import FastAPI, File, UploadFile

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
   file_path = f"uploaded_{file.filename}"
   with open(file_path, "wb") as f:
       f.write(content)
   return {"filename": file.filename, "size": len(content)}


#uvicorn app:app