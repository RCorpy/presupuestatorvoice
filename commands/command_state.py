# commands/command_state.py
import re
import os
from models.proforma_row import ProformaRow


def normalize_product_tokens(name: str) -> list[str]:
    """
    Convierte:
    'EPOXI RAL 7043 K-1'
    en:
    ['EPOXI', 'RAL', '7', '0', '4', '3', 'K', '1']
    """
    name = name.upper()

    tokens = []
    for part in re.findall(r"[A-Z]+|\d+", name):
        if part.isdigit():
            tokens.extend(list(part))  # 7043 → 7,0,4,3
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


class CommandState:
    MAIN_COMMANDS = ["FILA", "PRODUCTO", "CANTIDAD", "PRECIO", "CANCELAR", "SIGUIENTE"]

    WORD_TO_INT = {
        "UNO": 1, "DOS": 2, "TRES": 3, "CUATRO": 4, "CINCO": 5
    }

    def __init__(self, materials: dict):
        self.materials = materials
        self.current_command = None
        self.last_value = None
        self.active_row = 0  # fila activa
        self.product_buffer = []             # ["KIT", "EPOXI", ...]
        self.product_matches = []            # candidatos actuales
        self.in_product_mode = False
        self.material_tokens = {
            name: normalize_product_tokens(name)
            for name in self.materials.keys()
        }
        self.product_triggers = os.getenv(
            "PRODUCT_TRIGGER_WORDS", ""
        ).split(",")


    def reset(self):
        self.current_command = None
        self.last_value = None
        self.in_product_mode = False
        self.product_buffer.clear()
        self.product_matches.clear()

    def handle_word(self, word, model):
        word = word.upper()

        if (
            self.current_command is None
            and not self.in_product_mode
            and word in self.product_triggers
        ):
            self.in_product_mode = True
            self.product_buffer = [word]
            self.product_matches = [
                p for p in self.materials
                if word in self.material_tokens[p]
            ]
            return f"Modo producto: {word} ({len(self.product_matches)} candidatos)"

        word = normalize_spoken_number(word)
        if word.isdigit():
            token = word
        else:
            token = word

        max_rows = model.row_count()

        print(word)

        # -----------------------
        # CANCELAR (global)
        # -----------------------
        if word == "CANCELAR":
            self.reset()
            return "Comando cancelado"

        # -----------------------
        # MODO PRODUCTO
        # -----------------------
        if self.in_product_mode:
            return self._handle_product_word(word, model)

        # -----------------------
        # SIGUIENTE (normal)
        # -----------------------
        if word == "SIGUIENTE":
            self.active_row += 1
            if self.active_row >= model.row_count():
                # Crear nueva fila PRODUCT vacía
                model.add_row(ProformaRow(
                    type="PRODUCT",
                    col_0="",
                    col_1="",
                    col_2="",
                    col_3="",
                    col_4=""
                ))
                # Limpiar buffers de producto para que no se copie nada
                self.product_buffer.clear()
                self.product_matches.clear()
            return f"Fila siguiente ({self.active_row + 1})"


        # -----------------------
        # SIN COMANDO ACTIVO
        # -----------------------
        if self.current_command is None:

            # Producto directo (compatibilidad)
            if word in self.materials:
                model.set_product(self.active_row, word)
                model.set_price(self.active_row, self.materials[word]["price"])
                return f"Producto {word} asignado"

            # Activar comando
            if word in ["FILA", "CANTIDAD", "PRECIO"]:
                self.current_command = word
                return f"Comando {word} activo, esperando valor"

            # Activar modo producto
            if word == "PRODUCTO":
                self.in_product_mode = True
                self.product_buffer.clear()  # <-- vacía, no ponemos "EPOXI" ni nada
                self.product_matches = list(self.materials.keys())
                return "Modo producto activado"


            return f"Palabra no reconocida: {word}"

        # -----------------------
        # COMANDOS CON VALOR
        # -----------------------
        if self.current_command == "FILA":
            if word == "NUEVA":
                model.add_row(ProformaRow(
                    type="PRODUCT",
                    col_0="",
                    col_1="",
                    col_2="",
                    col_3="",
                    col_4=""
                ))
                self.active_row = model.row_count() - 1
                # Limpiar buffers para que no se arrastre producto previo
                self.product_buffer.clear()
                self.product_matches.clear()
                self.reset()
                return f"Fila nueva creada: {self.active_row + 1}"
            row_number = self.WORD_TO_INT.get(word)
            if row_number is None:
                try:
                    row_number = int(word)
                except ValueError:
                    self.reset()
                    return f"Valor inválido para FILA: {word}"

            if 1 <= row_number <= max_rows:
                self.active_row = row_number - 1
                self.reset()
                return f"Fila cambiada a {row_number}"
            else:
                self.reset()
                return f"Número de fila inválido: {word}"

        elif self.current_command == "CANTIDAD":
            numeric_value = self.WORD_TO_INT.get(word, word)
            try:
                numeric_value = int(numeric_value)
                model.set_quantity(self.active_row, numeric_value)
                self.reset()
                return f"Cantidad asignada: {numeric_value}"
            except ValueError:
                self.reset()
                return f"Cantidad inválida: {word}"

        elif self.current_command == "PRECIO":
            numeric_value = self.WORD_TO_INT.get(word, word)
            try:
                numeric_value = float(numeric_value)
                model.set_price(self.active_row, numeric_value)
                self.reset()
                return f"Precio asignado: {numeric_value}"
            except ValueError:
                self.reset()
                return f"Precio inválido: {word}"

        self.reset()
        return f"Error inesperado con palabra: {word}"

    def _handle_product_word(self, word, model):
        word = word.upper()

        # -----------------------
        # CONFIRMAR PRODUCTO
        # -----------------------
        if word == "SIGUIENTE":
            if len(self.product_matches) == 1:
                product = self.product_matches[0]
                model.set_product(self.active_row, product)
                model.set_price(self.active_row, self.materials[product]["price"])
                self.reset()
                return f"Producto {product} confirmado"
            else:
                return f"No se puede confirmar, candidatos: {len(self.product_matches)}"

        # -----------------------
        # AÑADIR TOKEN AL BUFFER
        # -----------------------
        self.product_buffer.append(word)

        new_matches = []

        for product in self.product_matches:
            product_tokens = self.material_tokens[product]

            # TODOS los tokens del buffer deben existir en el producto
            if all(token in product_tokens for token in self.product_buffer):
                new_matches.append(product)

        # -----------------------
        # SI NO HAY MATCH → ROLLBACK
        # -----------------------
        if not new_matches:
            self.product_buffer.pop()
            return f"Palabra no válida para producto: {word}"

        # -----------------------
        # ACTUALIZAR MATCHES
        # -----------------------
        self.product_matches = new_matches

        return (
            f"Producto parcial: {' '.join(self.product_buffer)} "
            f"({len(self.product_matches)} candidatos)"
        )

