# db/materials_repository.py
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("MATERIALS_DB_PATH", "materials.db")


def load_materials():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, price
        FROM Materials
        ORDER BY name
    """)
    rows = cur.fetchall()
    conn.close()

    # Diccionario indexado por nombre (MAYÚSCULAS)
    return {
        row["name"]: {
            "id": row["id"],
            "price": row["price"]
        }
        for row in rows
    }
