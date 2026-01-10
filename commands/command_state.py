import os
import re
from models.proforma_row import ProformaRow
from enum import Enum, auto



# --------------------------------------------------
# Helpers
# --------------------------------------------------

class CommandMode(Enum):
    IDLE = auto()
    PRODUCT = auto()
    QUANTITY = auto()
    PRICE = auto()
    ROW = auto()

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
        self.mode = CommandMode.IDLE
        self.number_buffer = ""

        # Producto
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

        # 1️⃣ Movimiento absoluto / prioridad
        self.MOVEMENT_COMMANDS = {
            "CANCELAR": self._cmd_cancel,
            "FILA": self._cmd_row,
            "SIGUIENTE": self._cmd_next,
        }

        # 2️⃣ Selección / edición de celda
        self.EDIT_COMMANDS = {
            "PRODUCTO": self._cmd_product_selection,
            "CANTIDAD": self._cmd_quantity,
            "PRECIO": self._cmd_price,
        }

        # 3️⃣ Subcomandos ROW / formato de fila
        self.ROW_SUBCOMMANDS = {
            "TITULO": self._cmd_title,
            "INFORMACION": self._cmd_info,
            "DETALLE": self._cmd_info,
            "PRODUCTO": self._cmd_product_row,
            "VACIA": self._cmd_empty,
            "BORRAR": self._cmd_delete,
        }
    # --------------------------------------------------

    def reset(self):
        self.mode = CommandMode.IDLE
        self.number_buffer = ""
        self.product_buffer.clear()
        self.product_matches.clear()

    # --------------------------------------------------

    def handle_word(self, word: str, model):
        word = normalize_spoken_number(word.upper())

        # ------------------------------
        # CANCELAR -> máxima prioridad
        # ------------------------------
        if word == "CANCELAR":
            return self._cmd_cancel(model)

        # ------------------------------
        # MODO ROW -> interceptar antes
        # ------------------------------
        if self.mode == CommandMode.ROW:
            # Subcomandos ROW
            if word in self.ROW_SUBCOMMANDS:
                result = self.ROW_SUBCOMMANDS[word](model)
                self.reset()
                return result

            # Número de fila
            row_number = self.WORD_TO_INT.get(word)
            if row_number is None:
                try:
                    row_number = int(word)
                except ValueError:
                    return f"Fila inválida: {word}"

            if 1 <= row_number <= model.row_count():
                self.active_row = row_number - 1
                self.reset()
                return f"Fila cambiada a {row_number}"
            else:
                return "Número de fila fuera de rango"

        # ------------------------------
        # MODO QUANTITY / PRICE
        # ------------------------------
        if self.mode in (CommandMode.QUANTITY, CommandMode.PRICE):
            return self._edit_number(word, model)

        # ------------------------------
        # MODO PRODUCT
        # ------------------------------
        if self.mode == CommandMode.PRODUCT:
            return self._handle_product_word(word, model)

        # ------------------------------
        # IDLE -> MOVIMIENTO
        # ------------------------------
        if word in self.MOVEMENT_COMMANDS:
            return self.MOVEMENT_COMMANDS[word](model)

        # ------------------------------
        # IDLE -> EDICIÓN
        # ------------------------------
        if word in self.EDIT_COMMANDS:
            return self.EDIT_COMMANDS[word](model)

        # ------------------------------
        # IDLE -> PRODUCT TRIGGERS
        # ------------------------------
# ------------------------------
# IDLE -> activar PRODUCT con token inicial
# ------------------------------
        if self.mode == CommandMode.IDLE and word in self.product_triggers:
            self.mode = CommandMode.PRODUCT
            self.product_buffer.clear()
            self.product_matches = list(self.materials.keys())
            return self._handle_product_word(word, model)


        # ------------------------------
        # IDLE -> PRODUCTO EXACTO
        # ------------------------------
        if word in self.product_triggers:
            self.mode = CommandMode.PRODUCT
            self.product_buffer = []
            self.product_matches = list(self.materials.keys())

            # 🔥 tratar el trigger como una palabra de producto normal
            return self._handle_product_word(word, model)


        # ------------------------------
        # NO RECONOCIDO
        # ------------------------------
        return f"Palabra no reconocida: {word}"

    # --------------------------------------------------
    # MÉTODOS PRIVADOS DE COMANDOS
    # --------------------------------------------------

    # --------------------------------------------------
    # MOVIMIENTO / PRIORIDAD
    # --------------------------------------------------
    def _cmd_cancel(self, model):
        self.reset()
        return "Comando cancelado"

    def _cmd_row(self, model):
        self.mode = CommandMode.ROW
        return "Modo FILA activo"

    # --------------------------------------------------
    # MOVIMIENTO / SIGUIENTE
    # --------------------------------------------------
    def _cmd_next(self, model):
        if self.mode in (CommandMode.QUANTITY, CommandMode.PRICE):
            # Delegar a _edit_number para confirmar valor
            return self._edit_number("SIGUIENTE", model)

        if self.mode == CommandMode.IDLE:
            # Avanzar fila
            self.move_or_create_row(model)
            return f"Fila siguiente ({self.active_row + 1})"

        # En ROW o cualquier otro modo no hacer nada
        return "SIGUIENTE no aplicable"


    # --------------------------------------------------
    # EDICIÓN DE CELDA
    # --------------------------------------------------
    def _cmd_product_selection(self, model):
        self.mode = CommandMode.PRODUCT
        self.product_buffer.clear()
        self.product_matches = list(self.materials.keys())
        return f"Modo PRODUCT activo ({len(self.product_matches)} candidatos)"

    def _cmd_quantity(self, model):
        self.mode = CommandMode.QUANTITY
        self.number_buffer = ""
        return "Modo CANTIDAD activado, dicta números"

    def _cmd_price(self, model):
        self.mode = CommandMode.PRICE
        self.number_buffer = ""
        return "Modo PRECIO activado, dicta números"

    # --------------------------------------------------
    # SUBCOMANDOS ROW
    # --------------------------------------------------
    def _cmd_title(self, model):
        row = model.get_row(self.active_row)
        row.type = "TITLE"
        # Solo columna visible para texto, no tocar cantidad/precio
        row.col_1 = row.col_1 or ""
        # no tocar col_2, col_3, col_4
        self.reset()
        return "Fila cambiada a TITULO"

    def _cmd_info(self, model):
        row = model.get_row(self.active_row)
        row.type = "INFO"
        # Solo las columnas que tengan sentido para INFO
        row.col_1 = row.col_1 or ""
        row.col_2 = row.col_2 or ""
        # col_3 y col_4 no tocar
        self.reset()
        return "Fila cambiada a DETALLE"


    def _cmd_empty(self, model):
        row = model.get_row(self.active_row)
        row.type = "EMPTY"
        row.col_1 = row.col_2 = row.col_3 = row.col_4 = ""
        self.reset()
        self.move_or_create_row(model)
        return "Fila vaciada"

    def _cmd_delete(self, model):
        model.remove_row(self.active_row)
        if model.row_count() == 0:
            model.add_row(ProformaRow(type="PRODUCT"))
            self.active_row = 0
        if self.active_row >= model.row_count():
            model.add_row(ProformaRow(type="PRODUCT"))
            self.active_row = model.row_count() - 1
        self.reset()
        return "Fila borrada"

    def _cmd_product_row(self, model):
        # PRODUCTO como subcomando de ROW
        self.mode = CommandMode.PRODUCT
        self.product_buffer.clear()
        self.product_matches = list(self.materials.keys())
        return f"Fila PRODUCTO activa ({len(self.product_matches)} candidatos)"

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

    # 🔥 CLAVE: SIEMPRE partir de TODOS los materiales
        matches = []
        for name in self.materials.keys():
            name_upper = name.upper()
            if all(token in name_upper for token in self.product_buffer):
                matches.append(name)

        self.product_matches = matches

        return (
            f"Producto parcial: {' '.join(self.product_buffer)} "
            f"({len(self.product_matches)} candidatos)"
        )
    
    def move_or_create_row(self, model):
        current_row = model.get_row(self.active_row)

        # -----------------------------------
        # CASO 1: venimos de INFO
        # -----------------------------------
        if current_row.type == "INFO":
            # Si es la última fila, aseguramos EMPTY debajo
            if self.active_row == model.row_count() - 1:
                model.add_row(ProformaRow(type="EMPTY"))

        # -----------------------------------
        # BUSCAR SIGUIENTE FILA ÚTIL
        # -----------------------------------
        next_row = self.active_row + 1

        # Saltar EMPTYs
        while next_row < model.row_count() and model.get_row(next_row).type == "EMPTY":
            next_row += 1

        # -----------------------------------
        # SI NO HAY FILA ÚTIL → crear PRODUCT
        # -----------------------------------
        if next_row >= model.row_count():
            model.add_row(ProformaRow(type="PRODUCT"))
            next_row = model.row_count() - 1

        self.active_row = next_row
        return f"Fila siguiente ({self.active_row + 1})"


    
    # --------------------------------------------------
# EDICIÓN DE CELDA: CANTIDAD / PRECIO
# --------------------------------------------------
    def _edit_number(self, word: str, model):
        word = word.upper()
        row = model.get_row(self.active_row)

        # 🔹 TITLE e INFO no aceptan cantidad/precio
        if row.type != "PRODUCT":
            return f"Fila {row.type} no admite cantidad/precio"

        # Separador decimal
        if word in ("COMA", "PUNTO"):
            if "." not in self.number_buffer:
                self.number_buffer += "."
                return f"Valor parcial: {self.number_buffer}"
            return "Ya hay un separador decimal"

        # Dígito hablado o numérico
        if word in self.WORD_TO_INT or word.isdigit():
            digit = str(self.WORD_TO_INT.get(word, word))
            self.number_buffer += digit
            if self.mode == CommandMode.QUANTITY:
                model.set_quantity(self.active_row, float(self.number_buffer))
            else:
                model.set_price(self.active_row, float(self.number_buffer))
            return f"Valor parcial: {self.number_buffer}"

        # SIGUIENTE confirma valor
        if word == "SIGUIENTE":
            if not self.number_buffer:
                # Sin valor -> avanzar
                if self.mode == CommandMode.QUANTITY:
                    self.mode = CommandMode.PRICE
                    self.number_buffer = ""
                    return "Sin cantidad, cambiando a PRECIO"
                elif self.mode == CommandMode.PRICE:
                    self.move_or_create_row(model)
                    self.reset()
                    return "Sin precio"
            else:
                value = float(self.number_buffer)
                if self.mode == CommandMode.QUANTITY:
                    model.set_quantity(self.active_row, value)
                    msg = f"Cantidad asignada: {value}"
                    self.mode = CommandMode.PRICE
                else:
                    model.set_price(self.active_row, value)
                    msg = f"Precio asignado: {value}"
                    self.move_or_create_row(model)
                    self.reset()
                self.number_buffer = ""
                return msg

        # Cambiar a PRODUCT
        if word in self.product_triggers:
            self.mode = CommandMode.PRODUCT
            self.product_buffer.clear()
            self.product_matches = list(self.materials.keys())
            return f"Modo PRODUCT activo ({len(self.product_matches)} candidatos)"

        # Cambiar a ROW
        if word == "FILA":
            self.mode = CommandMode.ROW
            return "Modo FILA activo"

        return f"Valor inválido: {word}"
