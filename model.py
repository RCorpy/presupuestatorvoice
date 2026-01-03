class ProformaModel:
    def __init__(self, rows=5):
        self.rows = rows
        self.data = [
            {
                "producto": "",
                "cantidad": "",
                "precio": "",
                "total": ""
            }
            for _ in range(rows)
        ]

    def set_producto(self, row, producto):
        self.data[row]["producto"] = producto

        # Intento automático de precio (stub)
        precio = self.get_precio_from_db(producto)
        if precio is not False:
            self.set_precio(row, precio)

    def set_cantidad(self, row, cantidad):
        self.data[row]["cantidad"] = cantidad
        self._recalculate(row)

    def set_precio(self, row, precio):
        self.data[row]["precio"] = precio
        self._recalculate(row)

    def get_precio_from_db(self, producto):
        """
        En el futuro:
        - Buscará el precio del producto en la base de datos
        - Tendrá en cuenta subcategorías (colores, etc.)
        Por ahora:
        - Devuelve False siempre
        """
        return False

    def _recalculate(self, row):
        try:
            cantidad = float(self.data[row]["cantidad"])
            precio = float(self.data[row]["precio"])
            self.data[row]["total"] = cantidad * precio
        except (ValueError, TypeError):
            self.data[row]["total"] = ""

    def row_count(self):
        return len(self.data)

    def add_row(self):
        self.data.append({
            "producto": "",
            "cantidad": "",
            "precio": "",
            "total": ""
        })