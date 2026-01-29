# db/proformas_repository.py

import sqlite3
import json
from datetime import datetime
from typing import List, Optional

from state.proforma_row import ProformaRow


DB_PATH = "database.db"


# -------------------------------------------------
# DB init
# -------------------------------------------------

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS proformas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        client_id INTEGER,

        area_m2 REAL,
        main_color TEXT,
        created_at TEXT,

        discount_percent REAL,
        shipping_cost REAL,

        table_rows_json TEXT,
        shipping_json TEXT,

        notes TEXT
    )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _serialize_rows(rows: List[ProformaRow]) -> str:
    data = []
    for row in rows:
        data.append({
            "type": row.type,
            "col_0": row.col_0,
            "col_1": row.col_1,
            "col_2": row.col_2,
            "col_3": row.col_3,
            "col_4": row.col_4,
        })
    return json.dumps(data, ensure_ascii=False)


def _deserialize_rows(json_text: str) -> List[ProformaRow]:
    data = json.loads(json_text)
    return [ProformaRow(**row_dict) for row_dict in data]


# -------------------------------------------------
# Public API
# -------------------------------------------------

def create_proforma(
    client_id: int,
    area_m2: float,
    main_color: str,
    discount_percent: float,
    shipping_cost: float,
    table_rows: List[ProformaRow],
    shipping_data: Optional[dict] = None,
    notes: Optional[str] = None,
) -> int:
    """
    Guarda una proforma y devuelve su ID.
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    created_at = datetime.now().isoformat()
    rows_json = _serialize_rows(table_rows)
    shipping_json = json.dumps(shipping_data, ensure_ascii=False) if shipping_data else None

    cur.execute("""
        INSERT INTO proformas (
            client_id,
            area_m2,
            main_color,
            created_at,
            discount_percent,
            shipping_cost,
            table_rows_json,
            shipping_json,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        client_id,
        area_m2,
        main_color,
        created_at,
        discount_percent,
        shipping_cost,
        rows_json,
        shipping_json,
        notes,
    ))

    proforma_id = cur.lastrowid

    conn.commit()
    conn.close()

    return proforma_id


def load_proforma_rows(proforma_id: int) -> List[ProformaRow]:
    """
    Carga SOLO las filas de una proforma para reconstruir la tabla.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT table_rows_json
        FROM proformas
        WHERE id = ?
    """, (proforma_id,))

    row = cur.fetchone()
    conn.close()

    if not row or not row[0]:
        return []

    return _deserialize_rows(row[0])


def get_proformas_for_client(client_id: int):
    """
    Devuelve una lista ligera para el selector de proformas.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, created_at, area_m2, main_color
        FROM proformas
        WHERE client_id = ?
        ORDER BY created_at DESC
    """, (client_id,))

    rows = cur.fetchall()
    conn.close()

    return rows

def search_proformas(query: str):
    """
    Búsqueda ligera por nombre o teléfono del cliente
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.id,
            c.name,
            c.phone,
            p.area_m2,
            p.main_color,
            p.created_at
        FROM proformas p
        JOIN clients c ON c.id = p.client_id
        WHERE c.name LIKE ? OR c.phone LIKE ?
        ORDER BY p.created_at DESC
    """, (f"%{query}%", f"%{query}%"))

    rows = cur.fetchall()
    conn.close()

    return rows
