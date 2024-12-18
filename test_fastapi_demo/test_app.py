import pytest
from fastapi.testclient import TestClient
from app import app
from db import create_item, get_items, delete_item
from faker import Faker
import sqlite3

client = TestClient(app)
fake = Faker()

@pytest.fixture(scope="function", autouse=True)
def clear_database():
    items = get_items()
    for item in items:
        delete_item(item["id"])

def test_index_redirect():
    response = client.get("/")
    assert response.status_code in [200, 303]
    assert "/items" in response.url

def test_update_item_page():
    response = client.post("/items/create", data={"name": "Test Item", "description": "Test Description"})
    assert response.status_code == 303

    items = get_items()
    item_id = items[0]["id"]

    response = client.get(f"/items/update/{item_id}")
    assert response.status_code == 200
    assert b"Update Item" in response.content

def test_search_empty_query():
    response = client.get("/items?query=NonExistentItem")
    assert response.status_code == 200
    assert b"No items found" in response.content

def test_create_item_empty_fields():
    response = client.post("/items/create", data={"name": "", "description": ""})
    assert response.status_code == 422

def test_empty_database():
    items = get_items()
    for item in items:
        delete_item(item["id"])
    items = get_items()
    assert len(items) == 0
