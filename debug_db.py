import sqlite3

conn = sqlite3.connect("database.db")  # usa el mismo DB_PATH
cur = conn.cursor()

cur.execute("SELECT id, table_rows_json FROM proformas")
for row in cur.fetchall():
    print(row)

conn.close()
