import sqlite3

# rutas
src_db = "materials.db"
dst_db = "database.db"

# abrir conexiones
src = sqlite3.connect(src_db)
dst = sqlite3.connect(dst_db)

src_cur = src.cursor()
dst_cur = dst.cursor()

# 1️⃣ borrar tabla clients vieja si existe
dst_cur.execute("DROP TABLE IF EXISTS clients")

# 2️⃣ crear tabla clients correcta
dst_cur.execute("""
CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    name TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    province TEXT,
    cp TEXT,
    cif TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
dst.commit()

# 3️⃣ leer datos de clients en materials.db
src_cur.execute("SELECT id, name, phone, email, address, city, province, cp, cif FROM clients")
rows = src_cur.fetchall()

# 4️⃣ insertarlos en database.db
for row in rows:
    dst_cur.execute("""
        INSERT INTO clients (id, name, phone, email, address, city, province, cp, cif)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, row)

dst.commit()
print(f"Se han migrado {len(rows)} clientes a database.db")

# cerrar conexiones
src.close()
dst.close()
