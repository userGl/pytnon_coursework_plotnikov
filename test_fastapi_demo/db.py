import sqlite3
from typing import List, Optional

DB_NAME = "items.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    )
    """)
    conn.commit()
    conn.close()

def get_items() -> List[dict]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    rows = c.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1], "description": row[2]} for row in rows]

def get_item(item_id: int) -> Optional[dict]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "description": row[2]}
    return None

def create_item(name: str, description: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO items (name, description) VALUES (?, ?)", (name, description))
    conn.commit()
    conn.close()

def update_item(item_id: int, name: str, description: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE items SET name = ?, description = ? WHERE id = ?", (name, description, item_id))
    conn.commit()
    conn.close()

def delete_item(item_id: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def search_items(query: str) -> List[dict]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE name LIKE ? OR description LIKE ?", ('%' + query + '%', '%' + query + '%'))
    rows = c.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1], "description": row[2]} for row in rows]
