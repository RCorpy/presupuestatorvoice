import sqlite3
import json
from datetime import datetime
from state.proforma_state import ProformaState
from services.proforma_serializer import ProformaSerializer

class ProformasRepository:
    def __init__(self, db_path="proformas.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def save(self, state: ProformaState, client_id: int,
             discount_percent=0, shipping_cost=0, proforma_date=None,
             total_price=None, total_m2=None, total_kg=None, main_color=None,
             overwrite_id: int | None = None):
        
        if proforma_date is None:
            proforma_date = datetime.now().date().isoformat()
        
        data_json = json.dumps(ProformaSerializer.to_dict(state), ensure_ascii=False)

        if overwrite_id:
            self.conn.execute("""
                UPDATE proformas SET
                    client_id=?, discount_percent=?, shipping_cost=?, proforma_date=?,
                    total_price=?, total_m2=?, total_kg=?, main_color=?, data_json=?
                WHERE id=?
            """, (client_id, discount_percent, shipping_cost, proforma_date,
                  total_price, total_m2, total_kg, main_color, data_json, overwrite_id))
            self.conn.commit()
            return overwrite_id
        else:
            cur = self.conn.execute("""
                INSERT INTO proformas (
                    client_id, discount_percent, shipping_cost, proforma_date,
                    total_price, total_m2, total_kg, main_color, data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (client_id, discount_percent, shipping_cost, proforma_date,
                  total_price, total_m2, total_kg, main_color, data_json))
            self.conn.commit()
            return cur.lastrowid

    def load(self, proforma_id: int) -> ProformaState:
        cur = self.conn.execute("SELECT data_json FROM proformas WHERE id=?", (proforma_id,))
        row = cur.fetchone()
        if not row:
            return None
        return ProformaSerializer.from_dict(json.loads(row["data_json"]))
