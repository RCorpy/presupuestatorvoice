# models/proforma_model.py
from models.proforma_row import ProformaRow
from db.materials_repository import load_materials


class ProformaModel:
    def __init__(self):
        self.rows: list[ProformaRow] = []
        self.materials = load_materials()  # cache en memoria

    # --------------------
    # Row management
    # --------------------

    def add_row(self, row: ProformaRow):
        self.rows.append(row)

    def insert_row(self, index: int, row: ProformaRow):
        self.rows.insert(index, row)

    def remove_row(self, index: int):
        if 0 <= index < len(self.rows):
            self.rows.pop(index)

    def row_count(self):
        return len(self.rows)

    def get_row(self, index) -> ProformaRow:
        return self.rows[index]

    # --------------------
    # Product helpers
    # --------------------

    def set_product(self, row_index: int, product_name: str):
        row = self.rows[row_index]
        if row.type != "PRODUCT":
            return
        row.col_1 = product_name

        price = self.get_price_from_db(product_name)
        if price is not None:
            row.col_3 = str(price)  # PRECIO UNITARIO
            self._recalculate(row)

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
        row.col_3 = str(price)  # PRECIO UNITARIO
        self._recalculate(row)

    # --------------------
    # Internals
    # --------------------

    def _recalculate(self, row: ProformaRow):
        try:
            qty = float(row.col_2)
            price = float(row.col_3)  # PRECIO UNITARIO
            row.col_4 = str(qty * price)  # TOTAL
        except (ValueError, TypeError):
            row.col_4 = ""

    def get_price_from_db(self, product_name: str):
        material = self.materials.get(product_name)
        if not material:
            return None
        return material.get("price")
