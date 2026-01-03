# commands/command_state.py

class CommandState:
    MAIN_COMMANDS = ["FILA", "PRODUCTO", "CANTIDAD", "PRECIO", "CANCELAR"]

    WORD_TO_INT = {
        "UNO": 1, "DOS": 2, "TRES": 3, "CUATRO": 4, "CINCO": 5
    }

    def __init__(self, materials: dict):
        self.materials = materials
        self.current_command = None
        self.last_value = None
        self.active_row = 0  # fila activa

    def reset(self):
        self.current_command = None
        self.last_value = None

    def handle_word(self, word, model):
        word = word.upper()
        max_rows = model.row_count()

        print(word)

        if word == "CANCELAR":
            self.reset()
            return "Comando cancelado"

        if word == "SIGUIENTE":
            self.active_row += 1
            if self.active_row >= model.row_count():
                model.add_row()
            return f"Fila siguiente ({self.active_row + 1})"

        # Comando principal
        if self.current_command is None:
            # Si no hay comando activo
            # ¿Es un producto?
            if word in self.materials:
                model.set_producto(self.active_row, word)
                model.set_precio(self.active_row, self.materials[word]["price"])
                return f"Producto {word} asignado"

            # ¿Es un comando explícito?
            elif word in ["FILA", "PRODUCTO", "CANTIDAD", "PRECIO"]:
                self.current_command = word
                return f"Comando {word} activo, esperando valor"
            else:
                return f"Palabra no reconocida en estado principal: {word}"

        # Ejecutar comando activo
        if self.current_command == "FILA":
            if word == "NUEVA":
                model.add_row()
                self.active_row = model.row_count() - 1
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

        elif self.current_command == "PRODUCTO":
            if word not in self.materials:
                #self.reset()
                return f"Producto no existente: {word}"

            price = self.materials[word]["price"]
            model.set_producto(self.active_row, word)
            model.set_precio(self.active_row, price)

            self.reset()
            return f"Producto {word} asignado"


        elif self.current_command == "CANTIDAD":
            numeric_value = self.WORD_TO_INT.get(word, word)
            try:
                numeric_value = int(numeric_value)
                model.set_cantidad(self.active_row, numeric_value)
                self.reset()
                return f"Cantidad asignada: {numeric_value}"
            except ValueError:
                self.reset()
                return f"Cantidad inválida: {word}"

        elif self.current_command == "PRECIO":
            numeric_value = self.WORD_TO_INT.get(word, word)
            try:
                numeric_value = float(numeric_value)
                model.set_precio(self.active_row, numeric_value)
                self.reset()
                return f"Precio asignado: {numeric_value}"
            except ValueError:
                self.reset()
                return f"Precio inválido: {word}"

        self.reset()
        return f"Error inesperado con palabra: {word}"
