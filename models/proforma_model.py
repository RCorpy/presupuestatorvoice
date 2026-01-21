# models/proforma_model.py
from models.proforma_row import ProformaRow
from db.materials_repository import load_materials
from copy import deepcopy
from models.row_factory import info_row
from generator.resin_config import get_product_info, RESIN_SYSTEMS
import re


class ProformaModel:
    def __init__(self, state=None):
        self.rows: list[ProformaRow] = []
        self.materials = load_materials()  # cache en memoria
        self.state = state

    # --------------------
    # Row management
    # --------------------

    def add_row(self, row: ProformaRow):
        # 🔹 Siempre añadir una copia independiente
        self.rows.append(deepcopy(row))

    def insert_row(self, index: int, row: ProformaRow):
        # 🔹 Siempre insertar una copia independiente
        self.rows.insert(index, deepcopy(row))

    def remove_row(self, index: int):
        if 0 <= index < len(self.rows):
            self.rows.pop(index)

    def row_count(self):
        return len(self.rows)

    def get_row(self, index) -> ProformaRow:
        return self.rows[index]

    def set_row(self, index: int, new_row: ProformaRow):
        if 0 <= index < len(self.rows):
            self.rows[index] = new_row


    # --------------------
    # Product helpers
    # --------------------

    def set_product(self, row_index: int, product_name: str, multiplier: float):
        row = self.get_row(row_index)
        if row.type != "PRODUCT":
            return

        row.col_1 = product_name

        base_price = self.get_price_from_db(product_name)
        if base_price is None:
            row.col_3 = "not found"
            return

        # Detectar tamaño del kit
        import re
        kit_multiplier = 1
        col0_lower = row.col_0.lower()
        match = re.search(r"\b(6|12|18|24)\b", col0_lower)
        if match:
            kit_multiplier = int(match.group(1))

        # Precio final
        unit_price = round(base_price * kit_multiplier * multiplier, 2)
        row.col_3 = str(unit_price)

        # Total = cantidad * unit_price
        try:
            qty = float(row.col_2)
        except:
            qty = 1
        row.col_4 = str(round(qty * unit_price, 2))







    def set_quantity(self, row_index: int, quantity):
        row = self.rows[row_index]
        if row.type != "PRODUCT":
            return
        row.col_2 = str(quantity)
        self._recalculate(row)

    def set_price(self, row_index: int, price):
        row = self.rows[row_index]
        if row.type != "PRODUCT":
            return
        row.col_3 = str(price)
        print("set_price", price)
        self._recalculate(row)

    # --------------------
    # Internals
    # --------------------

    def _recalculate(self, row: ProformaRow):
        if row.type != "PRODUCT":
            return
        try:
            qty = float(row.col_2)
            price = float(row.col_3)
            row.col_4 = str(qty * price)
        except (ValueError, TypeError):
            row.col_4 = ""


    def get_price_from_db(self, product_name: str):
        material = self.materials.get(product_name)
        if not material:
            return None
        return material.get("price")

    def _infer_info_from_product(self, product_name: str):
        """
        Devuelve la información asociada al sistema de resina.
        Solo si el producto pertenece a RESIN_SYSTEMS.
        """
        for system_key, data in RESIN_SYSTEMS.items():
            if system_key in product_name.upper() or data["product_base"] in product_name.upper():
                info = data.get("product_info")
                if info:
                    return info, ""
        return None, None

