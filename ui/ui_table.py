# ui/ui_table.py

from PySide6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QWidget,
    QLineEdit, QLabel, QPushButton, QListWidget
)
from PySide6.QtCore import Qt

from voice.voice_listener import VoiceListener
from voice.voice_normalizer import normalize_command
from voice.grammar_builder import build_grammar

from commands.command_state import CommandState
from excel.excel_exporter import export_proforma_to_excel
from db.materials_repository import load_materials

from models.proforma_model import ProformaModel
from models.proforma_row import ProformaRow


class ProformaTableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PresupuestatorVoice")
        self.resize(1100, 550)

        # --------------------------------------------------
        # Datos / estado
        # --------------------------------------------------
        self.materials = load_materials()
        self.model = ProformaModel()
        self.state = CommandState(self.materials)

        self.active_row = 0
        self.last_token = None
        self.listening = False
        self.voice_worker = None

        # --------------------------------------------------
        # Filas iniciales (ejemplo funcional)
        # --------------------------------------------------
        self.model.add_row(ProformaRow(type="TITLE", col_1="2 CAPAS EPOXI VERDE"))
        self.model.add_row(ProformaRow(
            type="PRODUCT",
            col_0="KIT 18 KG",
            col_1="KIT EPOXI VERDE",
            col_2="1",
            col_3="120",
            col_4="120"
        ))
        self.model.add_row(ProformaRow(
            type="INFO",
            col_1="CATALIZADOR 5:1",
            col_2="100% SÓLIDOS"
        ))
        self.model.add_row(ProformaRow(type="EMPTY"))

        # --------------------------------------------------
        # Barra lateral izquierda
        # --------------------------------------------------
        self.sidebar = QWidget()
        self.sidebar.setMaximumWidth(140)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setAlignment(Qt.AlignTop)

        # Botones de acciones sobre la tabla
        self.add_product_btn = QPushButton("➕ Producto")
        self.add_product_btn.clicked.connect(self.add_product_row)
        sidebar_layout.addWidget(self.add_product_btn)

        # Espacio flexible
        sidebar_layout.addStretch()

        # Botones globales
        self.listen_button = QPushButton("🎙️ Escuchar")
        self.listen_button.clicked.connect(self.listen_voice)
        sidebar_layout.addWidget(self.listen_button)

        self.excel_button = QPushButton("💾 Exportar Excel")
        self.excel_button.clicked.connect(self.export_excel)
        sidebar_layout.addWidget(self.excel_button)

        # --------------------------------------------------
        # Tabla
        # --------------------------------------------------
        self.table = QTableWidget(self.model.row_count(), 5)
        self.table.setHorizontalHeaderLabels(
            ["KITS", "PRODUCTO", "CANTIDAD", "PRECIO", "TOTAL"]
        )
        self._init_table_items()
        self.table.cellChanged.connect(self.on_cell_changed)
        self.table.cellClicked.connect(self.on_cell_clicked)

        # --------------------------------------------------
        # Lista de productos (ProductBuffer)
        # --------------------------------------------------
        self.product_list = QListWidget()
        self.product_list.setMaximumWidth(350)
        self.product_list.itemClicked.connect(self.on_product_clicked)
        self.product_list.hide()

        # --------------------------------------------------
        # Input de comandos
        # --------------------------------------------------
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText(
            "Ej: PRODUCTO KIT EPOXI PRIMER GRIS MEDIO"
        )
        self.command_input.returnPressed.connect(self.process_command)

        # --------------------------------------------------
        # Estado
        # --------------------------------------------------
        self.status_label = QLabel("Listo")

        # --------------------------------------------------
        # Layout principal
        # --------------------------------------------------
        table_layout = QVBoxLayout()
        table_layout.addWidget(self.table)
        table_layout.addWidget(self.status_label)
        table_layout.addWidget(self.command_input)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.sidebar)
        main_layout.addLayout(table_layout)
        main_layout.addWidget(self.product_list)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # --------------------------------------------------
        # Refresco inicial
        # --------------------------------------------------
        self.refresh_all_rows()
        self.highlight_active_row()
        



    # ======================================================
    # Tabla
    # ======================================================

    def _init_table_items(self):
        """Inicializa QTableWidgetItem en todas las celdas"""
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                if self.table.item(r, c) is None:
                    self.table.setItem(r, c, QTableWidgetItem(""))

    def highlight_active_row(self):
        for r in range(min(self.table.rowCount(), self.model.row_count())):
            row_type = self.model.get_row(r).type

            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item is None:
                    continue

                # fila activa
                if r == self.active_row:
                    item.setBackground(Qt.yellow)
                    item.setForeground(Qt.black)
                else:
                    # color según tipo
                    if row_type == "TITLE":
                        item.setBackground(Qt.blue)
                        item.setForeground(Qt.white)
                    elif row_type == "EMPTY":
                        item.setBackground(Qt.lightGray)
                        item.setForeground(Qt.black)
                    else:
                        item.setBackground(Qt.white)
                        item.setForeground(Qt.black)

    def on_cell_clicked(self, row, column):
        self.active_row = row
        self.state.active_row = row
        self.highlight_active_row()
        self.update_product_suggestions()

    def refresh_row(self, row_index):
        self.table.blockSignals(True)
        row = self.model.get_row(row_index)

        # asegurar items existen
        for c in range(self.table.columnCount()):
            if self.table.item(row_index, c) is None:
                self.table.setItem(row_index, c, QTableWidgetItem(""))

        # TITLE
        if row.type == "TITLE":
            item = self.table.item(row_index, 0)
            item.setText(row.col_1)
            item.setBackground(Qt.blue)
            item.setForeground(Qt.black)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        # PRODUCT
        elif row.type == "PRODUCT":
            values = [row.col_0, row.col_1, row.col_2, row.col_3, row.col_4]
            for c, value in enumerate(values):
                item = self.table.item(row_index, c)
                if item:
                    item.setText(value or "")

            # columna TOTAL no editable
            total_item = self.table.item(row_index, 4)
            if total_item:
                total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)

        # INFO
        elif row.type == "INFO":
            item0 = self.table.item(row_index, 0)
            item1 = self.table.item(row_index, 1)
            if item0: item0.setText(row.col_1 or "")
            if item1: item1.setText(row.col_2 or "")
            for item in (item0, item1):
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        # EMPTY → marcar gris o highlight si activa
        elif row.type == "EMPTY":
            for c in range(self.table.columnCount()):
                item = self.table.item(row_index, c)
                if item:
                    item.setText("")
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    if row_index == self.active_row:
                        # fila activa → amarillo
                        item.setBackground(Qt.yellow)
                        item.setForeground(Qt.black)
                    else:
                        # fila normal → gris
                        item.setBackground(Qt.lightGray)
                        item.setForeground(Qt.black)

        self.table.blockSignals(False)

    def refresh_all_rows(self):
        for r in range(self.model.row_count()):
            self.refresh_row(r)

    def sync_table_rows(self):
        """Añade filas nuevas al QTableWidget si el modelo creció"""
        current_table_rows = self.table.rowCount()
        model_rows = self.model.row_count()
        if model_rows > current_table_rows:
            self.table.setRowCount(model_rows)
            for r in range(current_table_rows, model_rows):
                for c in range(self.table.columnCount()):
                    if self.table.item(r, c) is None:
                        self.table.setItem(r, c, QTableWidgetItem(""))

    def on_cell_changed(self, row, column):
        """Actualiza los datos del modelo cuando el usuario edita la celda"""
        proforma_row = self.model.get_row(row)
        if proforma_row.type != "PRODUCT":
            return

        text = self.table.item(row, column).text() or ""

        if column == 0:
            # Columna 0 → KITS
            proforma_row.col_0 = text
        elif column == 1:
            # Columna 1 → Nombre producto
            self.model.set_product(row, text)
            # Auto-asignar precio unitario si existe
            price = self.model.get_price_from_db(text)
            if price is not None:
                self.model.set_price(row, price)
        elif column == 2:
            # Columna 2 → Cantidad
            self.model.set_quantity(row, text)
        elif column == 3:
            # Columna 3 → Precio unitario
            self.model.set_price(row, text)

        # Total siempre se recalcula en set_quantity o set_price
        self.refresh_row(row)


    # ======================================================
    # Comandos (texto / voz)
    # ======================================================

    def process_command(self):
        text = self.command_input.text().upper()
        self.command_input.clear()
        self._process_tokens(text.split())

    def listen_voice(self):
        if not self.listening:
            self.listening = True
            self.listen_button.setText("⏹️ Parar")
            grammar = build_grammar(self.materials)
            self.voice_worker = VoiceListener(grammar=grammar)
            self.voice_worker.result_ready.connect(self.on_voice_result)
            self.voice_worker.start()
        else:
            self.listening = False
            self.listen_button.setText("🎙️ Escuchar")
            if self.voice_worker:
                self.voice_worker.stop()
                self.voice_worker = None

    def on_voice_result(self, text):
        normalized = normalize_command(text)
        self._process_tokens(normalized.split())
        self.refresh_all_rows()

    def _process_tokens(self, tokens):
        repeat_allowed = ["SIGUIENTE", "NUEVA", "PRODUCTO", "KIT", "EPOXI"]

        for token in tokens:
            if token == self.last_token and token not in repeat_allowed:
                continue
            self.last_token = token

            before_rows = self.model.row_count()

            msg = self.state.handle_word(token, self.model)

            after_rows = self.model.row_count()

            self.active_row = self.state.active_row
            self.status_label.setText(msg)

            # 🔴 CLAVE: si el modelo cambió, refrescar TODO
            if after_rows != before_rows:
                self.sync_table_rows()
                self.refresh_all_rows()
            else:
                self.refresh_row(self.active_row)

            self.highlight_active_row()
            self.highlight_active_cell()
            self.update_product_suggestions()

    # ======================================================
    # ProductBuffer UI
    # ======================================================

    def update_product_suggestions(self):
        self.product_list.clear()
        if not self.state.in_product_mode:
            self.product_list.hide()
            return
        self.product_list.show()
        for product in self.state.product_matches[:50]:
            self.product_list.addItem(product)

    def on_product_clicked(self, item):
        product = item.text()
        self.model.set_product(self.state.active_row, product)
        price = self.model.get_price_from_db(product)
        if price is not None:
            self.model.set_price(self.state.active_row, price)

        # Resetear estado
        self.state.reset()
        self.product_list.clear()
        self.product_list.hide()

        # Sincronizar tabla con el modelo
        self.sync_table_rows()

        # Refrescar todas las filas relevantes
        self.refresh_all_rows()
        self.highlight_active_row()


    # ======================================================
    # Excel
    # ======================================================

    def export_excel(self):
        try:
            path = export_proforma_to_excel(self.model)
            self.status_label.setText(f"Excel creado: {path}")
        except Exception as e:
            self.status_label.setText(f"Error exportando Excel: {e}")

    def add_product_row(self):
        insert_at = self.active_row + 1

        self.model.insert_row(insert_at, ProformaRow(type="PRODUCT"))

        self.sync_table_rows()
        self.refresh_all_rows()

        self.active_row = insert_at
        self.state.active_row = insert_at
        self.highlight_active_row()

    def highlight_active_cell(self):
        if self.state.current_command == "CANTIDAD":
            col = 2
        elif self.state.current_command == "PRECIO":
            col = 3
        else:
            return

        item = self.table.item(self.active_row, col)
        if item:
            item.setBackground(Qt.cyan)

