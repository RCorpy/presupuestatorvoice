# models/proforma_model.py
from models.proforma_row import ProformaRow
from db.materials_repository import load_materials
from copy import deepcopy


PRODUCT_INFO_RULES = {
    "EPOXI": "Catalizador 5:1",
    "POLITOP": "Resina monocomponente",
}


class ProformaModel:
    def __init__(self):
        self.rows: list[ProformaRow] = []
        self.materials = load_materials()  # cache en memoria

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


    # --------------------
    # Product helpers
    # --------------------

    def set_product(self, row_index: int, product_name: str):
        row = self.rows[row_index]
        if row.type != "PRODUCT":
            return

        row.col_1 = product_name

        # Precio unitario
        price = self.get_price_from_db(product_name)
        if price is not None:
            row.col_3 = str(price)
            self._recalculate(row)

        # ----------------------
        # Agregar INFO si aplica
        # ----------------------
        info_text = self._infer_info_from_product(product_name)
        if info_text:
            # Solo insertamos si la siguiente fila no es INFO ya
            if row_index + 1 >= len(self.rows) or self.rows[row_index + 1].type != "INFO":
                self.insert_row(
                    row_index + 1,
                    ProformaRow(type="INFO", col_1=info_text)
                )


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

    def _infer_info_from_product(self, product_name):
        for key, text in PRODUCT_INFO_RULES.items():
            if key in product_name:
                return text
        return None