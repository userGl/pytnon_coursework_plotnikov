from fastapi import FastAPI, Form, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from db import create_item, update_item, delete_item, get_items, get_item, search_items, create_table
from typing import Optional
from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Создаем таблицу при старте приложения
create_table()

@app.get("/", response_class=RedirectResponse)
def index():
    return RedirectResponse(url="/items")

@app.get("/items")
def read_items(request: Request, query: Optional[str] = None):
    items = search_items(query) if query else get_items()
    return templates.TemplateResponse("index.html", {"request": request, "items": items, "query": query})

@app.get("/items/create")
def create_item_page(request: Request):
    return templates.TemplateResponse("create_item.html", {"request": request})

@app.post("/items/create")
def create_item_action(name: str = Form(...), description: str = Form(...)):
    create_item(name, description)
    return RedirectResponse(url="/items", status_code=303)

@app.get("/items/update/{item_id}")
def update_item_page(request: Request, item_id: int):
    item = get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return templates.TemplateResponse("update_item.html", {"request": request, "item": item})

@app.post("/items/update/{item_id}")
def update_item_action(item_id: int, name: str = Form(...), description: str = Form(...)):
    update_item(item_id, name, description)
    return RedirectResponse(url="/items", status_code=303)

@app.post("/items/delete/{item_id}")
def delete_item_action(item_id: int):
    delete_item(item_id)
    return RedirectResponse(url="/items", status_code=303)
