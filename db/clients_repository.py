import sqlite3
from datetime import datetime

DB_PATH = "materials.db"


def _get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT,
            phone TEXT UNIQUE,

            email TEXT,
            cif TEXT,

            address TEXT,
            cp TEXT,
            city TEXT,
            province TEXT,

            created_at TEXT,
            updated_at TEXT
        )
    """)

    conn.commit()
    conn.close()

# -------------------------------------------------
# BÚSQUEDA
# -------------------------------------------------

def get_matches(phone: str = "", name: str = ""):
    conn = _get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if phone:
        cur.execute("""
            SELECT * FROM clients
            WHERE phone LIKE ?
            ORDER BY name
            LIMIT 20
        """, (f"%{phone}%",))
    else:
        cur.execute("""
            SELECT * FROM clients
            WHERE name LIKE ?
            ORDER BY name
            LIMIT 20
        """, (f"%{name}%",))

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# -------------------------------------------------
# CREAR O EDITAR
# -------------------------------------------------

# returns: "created" | "updated" | "unchanged"
def create_or_update_client(data: dict) -> str:
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM clients WHERE phone = ?", (data["phone"],))
    row = cur.fetchone()

    if row is None:
        cur.execute(
            """
            INSERT INTO clients (name, phone, email, cif, address, cp, city, province)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["name"],
                data["phone"],
                data["email"],
                data["cif"],
                data["address"],
                data["cp"],
                data["city"],
                data["province"],
            )
        )
        conn.commit()
        conn.close()
        return "created"

    # cliente existe → comprobamos cambios
    columns = ["name", "phone", "email", "cif", "address", "cp", "city", "province"]
    existing = dict(zip(columns, row[1:]))

    changed = any(existing[k] != data[k] for k in columns)

    if not changed:
        conn.close()
        return "unchanged"

    cur.execute(
        """
        UPDATE clients
        SET name=?, email=?, cif=?, address=?, cp=?, city=?, province=?
        WHERE phone=?
        """,
        (
            data["name"],
            data["email"],
            data["cif"],
            data["address"],
            data["cp"],
            data["city"],
            data["province"],
            data["phone"],
        )
    )

    conn.commit()
    conn.close()
    return "updated"



def client_exists(phone: str) -> bool:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM clients WHERE phone = ?", (phone,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists


init_db()