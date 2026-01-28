import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Client:
    id: int | None = None
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    province: str | None = None
    postal_code: str | None = None
    country: str | None = None
    cif: str | None = None
    contact: str | None = None

class ClientsRepository:
    def __init__(self, db_path="proformas.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def search(self, name=None, phone=None):
        query = "SELECT * FROM clients WHERE 1=1"
        params = []
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if phone:
            query += " AND phone LIKE ?"
            params.append(f"%{phone}%")
        query += " ORDER BY name LIMIT 20"
        cur = self.conn.execute(query, params)
        return [Client(**dict(row)) for row in cur.fetchall()]

    def create_or_update(self, client: Client):
        now = datetime.now().isoformat()
        if client.id:
            # Update existing
            self.conn.execute("""
                UPDATE clients SET
                    name = ?, phone = ?, email = ?, address = ?, city = ?,
                    province = ?, postal_code = ?, country = ?, cif = ?, contact = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                client.name, client.phone, client.email, client.address, client.city,
                client.province, client.postal_code, client.country, client.cif, client.contact,
                now, client.id
            ))
            self.conn.commit()
            return client.id
        else:
            # Insert new
            cur = self.conn.execute("""
                INSERT INTO clients (
                    name, phone, email, address, city, province,
                    postal_code, country, cif, contact, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client.name, client.phone, client.email, client.address, client.city,
                client.province, client.postal_code, client.country, client.cif, client.contact,
                now
            ))
            self.conn.commit()
            return cur.lastrowid
