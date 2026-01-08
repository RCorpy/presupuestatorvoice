import os
import re
from models.proforma_row import ProformaRow



# --------------------------------------------------
# Helpers
# --------------------------------------------------

def normalize_product_tokens(name: str) -> list[str]:
    """
    'EPOXI RAL 7043 K-1'
    -> ['EPOXI', 'RAL', '7', '0', '4', '3', 'K', '1']
    """
    name = name.upper()
    tokens = []

    for part in re.findall(r"[A-Z]+|\d+", name):
        if part.isdigit():
            tokens.extend(list(part))
        else:
            tokens.append(part)

    return tokens


def normalize_spoken_number(word: str) -> str:
    WORD_TO_DIGIT = {
        "CERO": "0",
        "UNO": "1",
        "DOS": "2",
        "TRES": "3",
        "CUATRO": "4",
        "CINCO": "5",
        "SEIS": "6",
        "SIETE": "7",
        "OCHO": "8",
        "NUEVE": "9",
    }
    return WORD_TO_DIGIT.get(word, word)


# --------------------------------------------------
# CommandState
# --------------------------------------------------

class CommandState:
    WORD_TO_INT = {
        "UNO": 1, "DOS": 2, "TRES": 3, "CUATRO": 4,
        "CINCO": 5, "SEIS": 6, "SIETE": 7,
        "OCHO": 8, "NUEVE": 9,
    }

    def __init__(self, materials: dict):
        self.materials = materials

        self.active_row = 0
        self.current_command = None

        # Producto
        self.in_product_mode = False
        self.product_buffer: list[str] = []
        self.product_matches: list[str] = []

        self.material_tokens = {
            name: normalize_product_tokens(name)
            for name in self.materials.keys()
        }

        self.product_triggers = [
            t.strip().upper()
            for t in os.getenv("PRODUCT_TRIGGER_WORDS", "PRODUCTO").split(",")
        ]

    # --------------------------------------------------

    def reset(self):
        self.current_command = None
        self.in_product_mode = False
        self.product_buffer.clear()
        self.product_matches.clear()

    # --------------------------------------------------

    def handle_word(self, word: str, model):
        word = word.upper()
        word = normalize_spoken_number(word)

        print("WORD:", word)

        # ==================================================
        # COMANDOS ESTRUCTURALES (PRIORIDAD ABSOLUTA)
        # ==================================================

        if word == "TITULO":
            row = model.get_row(self.active_row)
            row.type = "TITLE"
            row.col_1 = ""
            row.col_2 = ""
            row.col_3 = ""
            row.col_4 = ""
            self.reset()
            return "Fila cambiada a TITULO"

        if word in ("INFORMACION", "DETALLE"):
            row = model.get_row(self.active_row)
            row.type = "INFO"
            row.col_1 = ""
            row.col_2 = ""
            row.col_3 = ""
            row.col_4 = ""
            self.reset()
            return "Fila cambiada a DETALLE"

        if word == "VACIA":
            row = model.get_row(self.active_row)
            row.type = "EMPTY"
            row.col_1 = ""
            row.col_2 = ""
            row.col_3 = ""
            row.col_4 = ""
            self.reset()
            return "Fila vaciada"

        # ==================================================
        # CANCELAR
        # ==================================================

        if word == "CANCELAR":
            self.reset()
            return "Comando cancelado"

        # ==================================================
        # MODO PRODUCTO
        # ==================================================

        if self.in_product_mode:
            return self._handle_product_word(word, model)

        # ==================================================
        # SIGUIENTE
        # ==================================================

        if word == "SIGUIENTE":
            current_row_type = model.get_row(self.active_row).type

            # Si la fila actual es INFO o DETALLE
            if current_row_type in ("INFO", "DETALLE"):
                # Comprobar si la siguiente fila existe y es EMPTY
                if self.active_row + 1 >= model.row_count() or model.get_row(self.active_row + 1).type != "EMPTY":
                    model.insert_row(
                        self.active_row + 1,
                        ProformaRow(type="EMPTY")
                    )
                self.active_row += 1  # movernos a la fila EMPTY creada o ya existente

            # Avanzar hasta la siguiente fila que no sea EMPTY
            next_row = self.active_row + 1
            while next_row < model.row_count() and model.get_row(next_row).type == "EMPTY":
                next_row += 1

            # Si llegamos al final, crear nueva PRODUCT
            if next_row >= model.row_count():
                model.add_row(ProformaRow(type="PRODUCT"))
                next_row = model.row_count() - 1

            self.active_row = next_row
            self.reset()
            return f"Fila siguiente ({self.active_row + 1})"




        # ==================================================
        # SIN COMANDO ACTIVO
        # ==================================================

        if self.current_command is None:

            # Activar modo producto
            if word in self.product_triggers:
                self.in_product_mode = True
                self.product_buffer.clear()
                self.product_matches = list(self.materials.keys())
                return "Modo producto activado"

            # Producto directo (compatibilidad)
            if word in self.materials:
                model.set_product(self.active_row, word)
                model.set_price(
                    self.active_row,
                    self.materials[word]["price"]
                )
                return f"Producto {word} asignado"

            # Activar comandos con valor
            if word in ("FILA", "CANTIDAD", "PRECIO"):
                self.current_command = word
                return f"Comando {word} activo"

            return f"Palabra no reconocida: {word}"

        # ==================================================
        # COMANDOS CON VALOR
        # ==================================================

        if self.current_command == "FILA":
            if word == "NUEVA":
                model.add_row(ProformaRow(type="PRODUCT"))
                self.active_row = model.row_count() - 1
                self.reset()
                return f"Fila nueva creada ({self.active_row + 1})"

            row_number = self.WORD_TO_INT.get(word)
            if row_number is None:
                try:
                    row_number = int(word)
                except ValueError:
                    self.reset()
                    return f"Fila inválida: {word}"

            if 1 <= row_number <= model.row_count():
                self.active_row = row_number - 1
                self.reset()
                return f"Fila cambiada a {row_number}"

            self.reset()
            return "Número de fila fuera de rango"

        if self.current_command == "CANTIDAD":
            try:
                value = int(self.WORD_TO_INT.get(word, word))
                model.set_quantity(self.active_row, value)
                self.reset()
                return f"Cantidad asignada: {value}"
            except ValueError:
                self.reset()
                return f"Cantidad inválida: {word}"

        if self.current_command == "PRECIO":
            try:
                value = float(self.WORD_TO_INT.get(word, word))
                model.set_price(self.active_row, value)
                self.reset()
                return f"Precio asignado: {value}"
            except ValueError:
                self.reset()
                return f"Precio inválido: {word}"

        self.reset()
        return f"Error inesperado con palabra: {word}"

    # --------------------------------------------------
    # PRODUCT MODE
    # --------------------------------------------------

    def _handle_product_word(self, word: str, model):
        word = word.upper()

        # Confirmar producto
        if word == "SIGUIENTE":
            if len(self.product_matches) == 1:
                product = self.product_matches[0]
                model.set_product(self.active_row, product)
                model.set_price(
                    self.active_row,
                    self.materials[product]["price"]
                )
                self.reset()
                return f"Producto {product} confirmado"
            return f"{len(self.product_matches)} candidatos, sigue acotando"

        # Añadir token
        self.product_buffer.append(word)

        new_matches = []
        for product in self.product_matches:
            tokens = self.material_tokens[product]
            if all(t in tokens for t in self.product_buffer):
                new_matches.append(product)

        if not new_matches:
            self.product_buffer.pop()
            return f"Token no válido: {word}"

        self.product_matches = new_matches
        return (
            f"Producto parcial: {' '.join(self.product_buffer)} "
            f"({len(self.product_matches)} candidatos)"
        )
    
