import sqlite3
import json

DB_PATH = "database.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1️⃣ Añadir columna 'shipping_data' si no existe
    try:
        cur.execute("ALTER TABLE proformas ADD COLUMN shipping_data TEXT")
        print("Columna 'shipping_data' añadida correctamente.")
    except sqlite3.OperationalError:
        print("La columna 'shipping_data' ya existe, seguimos.")

    # 2️⃣ Obtener todas las proformas
    cur.execute("SELECT id FROM proformas")
    proformas = cur.fetchall()

    # 3️⃣ Inicializar shipping_data como vacío JSON
    for (pid,) in proformas:
        empty_shipping = json.dumps({
            "contact": "",
            "address": "",
            "postal_code": "",
            "city": "",
            "province": "",
            "phone": "",
            "notes": ""
        }, ensure_ascii=False)
        cur.execute("UPDATE proformas SET shipping_data = ? WHERE id = ?", (empty_shipping, pid))

    conn.commit()
    conn.close()
    print("Columna 'shipping_data' inicializada para todas las proformas.")

if __name__ == "__main__":
    main()
