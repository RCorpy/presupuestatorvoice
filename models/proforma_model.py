# models/proforma_model.py
from models.proforma_row import ProformaRow
from db.materials_repository import load_materials
from copy import deepcopy
from models.row_factory import info_row
from generator.resin_config import get_product_info, RESIN_SYSTEMS, PACKAGING_COST_PER_PHASE, get_kit_base
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
        self.rows.append(row)

    def insert_row(self, index: int, row: ProformaRow):
        # 🔹 Siempre insertar una copia independiente
        self.rows.insert(index, row)

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

    def clear(self):
        """Vacía completamente la proforma"""
        self.rows.clear()


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

        # Detectar tamaño del kit (cualquier número entero en col_0)
        import re
        kit_multiplier = 1
        col0_lower = row.col_0.lower()
        match = re.search(r"\b(\d+)\b", col0_lower)
        if match:
            try:
                kit_multiplier = int(match.group(1))
            except ValueError:
                kit_multiplier = 1
        # determinar la base de kits del producto para convertir el coste de envase a por kg
        _, sys_key = self._infer_info_from_product(product_name)
        kit_base = get_kit_base(sys_key) if sys_key else 6
        packaging_price = kit_multiplier * PACKAGING_COST_PER_PHASE / kit_base
        # Precio final
        unit_price = round((base_price * kit_multiplier * multiplier) + packaging_price, 2) 
        row.col_3 = str(unit_price)

        # Total = cantidad * unit_price
        try:
            qty = float(row.col_2)
        except:
            qty = 1
        row.col_4 = str(round(qty * unit_price, 2))

        info, sys_key = self._infer_info_from_product(product_name)

        if info:
            next_index = row_index + 1

            # Caso 1: fila INFO ya existe debajo
            if next_index < len(self.rows) and self.rows[next_index].type == "INFO":
                if not self.rows[next_index].col_0:
                    self.rows[next_index].col_0 = info
                print("caso 1")

            # Caso último índice → primero añadir fila PRODUCT temporal AQUI DA ERROR YA QUE NO ESCRIBE INFO
            elif next_index >= len(self.rows):
                temp_product = ProformaRow(type="PRODUCT")  # fila temporal para “no ser la última”
                self.rows.append(temp_product)
                print("fila PRODUCT temporal añadida", info)

                # Ahora crear fila INFO debajo
                info_row = ProformaRow(type="INFO")
                info_row.col_0 = info
                self.insert_row(next_index, info_row)
                self.rows[next_index].col_0 = info
                print("caso último índice: INFO creada")

            # Caso siguiente fila no es INFO → insertar antes de ella
            else:
                info_row = ProformaRow(type="INFO")
                info_row.col_0 = info
                self.insert_row(next_index, info_row)
                print("caso 2 (inserción en medio)")










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
            row.col_4 =  str(round(qty * price, 2))
        except (ValueError, TypeError):
            row.col_4 = ""


    def get_price_from_db(self, product_name: str):
        material = self.materials.get(product_name)
        if not material:
            return None
        return material.get("price")

    def _infer_info_from_product(self, product_name: str):
        """
        Devuelve una tupla (info, system_key) correspondiente al sistema de resina
        identificado por el nombre de producto. info puede ser None si no hay
        texto adicional. system_key será None si no se encuentra el sistema.
        """
        for system_key, data in RESIN_SYSTEMS.items():
            if system_key in product_name.upper() or data["product_base"] in product_name.upper():
                info = data.get("product_info")
                return info, system_key
        return None, None

    def get_total_price(self) -> float:
        total = 0.0
        for row in self.rows:
            if row.type == "PRODUCT":
                try:
                    qty = float(row.col_2) if row.col_2 else 0
                    price = float(row.col_3) if row.col_3 else 0
                    total += qty * price
                except ValueError:
                    pass
        return round(total, 2)

    def get_total_kg(self) -> float:
        total_kg = 0.0
        for row in self.rows:
            if row.type == "PRODUCT":
                try:
                    kit_size = float(row.col_0.replace("kg", "").strip())
                    qty = float(row.col_2)
                    total_kg += kit_size * qty
                except:
                    pass
        return round(total_kg, 2)

    def get_price_per_m2(self, area_m2: float) -> float:
        if area_m2 <= 0:
            return 0.0
        return round(self.get_total_price() / area_m2, 2)

    def get_kg_per_m2(self, area_m2: float) -> float:
        if area_m2 <= 0:
            return 0.0
        return round(self.get_total_kg() / area_m2, 3)
    
    def get_kg_by_phase(self):
        kg_imprimacion = 0.0
        kg_capas = 0.0
        current_phase = None

        for row in self.rows:
            if row.type == "TITLE":
                title = row.col_0.upper()
                if "IMPRIMACION" in title:
                    current_phase = "IMPRIMACION"
                elif "CAPA" in title:
                    current_phase = "CAPAS"
                else:
                    current_phase = None

            elif row.type == "PRODUCT" and current_phase:
                try:
                    kit_size = float(row.col_0.replace("kg", "").strip())
                    qty = float(row.col_2)
                    kg = kit_size * qty

                    if current_phase == "IMPRIMACION":
                        kg_imprimacion += kg
                    elif current_phase == "CAPAS":
                        kg_capas += kg
                except:
                    pass

        return round(kg_imprimacion, 2), round(kg_capas, 2)

    def get_g_m2_by_phase(self, area_m2: float):
        if area_m2 <= 0:
            return 0, 0

        kg_imp, kg_cap = self.get_kg_by_phase()

        g_m2_imp = round((kg_imp * 1000) / area_m2, 1)
        g_m2_cap = round((kg_cap * 1000) / area_m2, 1)

        return g_m2_imp, g_m2_cap

    def get_total_g_m2(self, area_m2: float):
        if area_m2 <= 0:
            return 0.0
        return round((self.get_total_kg() * 1000) / area_m2, 1)

    def update_row_from_ui(self, row_index: int, col_0=None, col_1=None, col_2=None, col_3=None):
        """
        Actualiza una fila del modelo con los datos que vienen de la UI
        y recalcula el TOTAL y otros valores derivados.
        """
        row = self.get_row(row_index)

        if not row:
            return

        if row.type == "INFO":
            if col_0 is not None:
                row.col_0 = col_0
            return

        if col_0 is not None:
            row.col_0 = col_0
        if col_1 is not None:
            row.col_1 = col_1
        if col_2 is not None:
            row.col_2 = str(col_2)
        if col_3 is not None:
            row.col_3 = str(col_3)

        # 🔹 Recalcular total
        try:
            qty = float(row.col_2) if row.col_2 else 1
            price = float(row.col_3) if row.col_3 else 0
            row.col_4 = str(round(qty * price, 2))
        except ValueError:
            row.col_4 = "0"