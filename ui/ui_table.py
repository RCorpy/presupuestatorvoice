# ui/ui_table.py

from PySide6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QWidget, QGridLayout,
    QLineEdit, QLabel, QPushButton, QListWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from voice.voice_listener import VoiceListener
from voice.voice_normalizer import normalize_command
from voice.grammar_builder import build_grammar

from commands.command_state import CommandState
from commands.command_state import CommandMode
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
        # Filas iniciales
        # --------------------------------------------------
        self.model.add_row(ProformaRow(type="PRODUCT"))

        # --------------------------------------------------
        # Barra lateral izquierda
        # --------------------------------------------------
        self.sidebar = QWidget()
        self.sidebar.setMaximumWidth(140)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setAlignment(Qt.AlignTop)
        sidebar_layout.setSpacing(10)

        # --- Botones principales ---
        self.add_product_btn = QPushButton("➕")
        self.add_product_btn.setFixedSize(40, 40)
        self.add_product_btn.setToolTip("Añadir fila PRODUCT")
        self.add_product_btn.clicked.connect(self.add_product_row)
        sidebar_layout.addWidget(self.add_product_btn, alignment=Qt.AlignHCenter)

        self.delete_row_btn = QPushButton("🗑️")
        self.delete_row_btn.setFixedSize(40, 40)
        self.delete_row_btn.setToolTip("Borrar fila actual")
        self.delete_row_btn.clicked.connect(self.delete_current_row)
        sidebar_layout.addWidget(self.delete_row_btn, alignment=Qt.AlignHCenter)

        # Separador
        sidebar_layout.addSpacing(15)

        # --- Grid tipos de fila ---
        type_grid = QGridLayout()
        type_grid.setSpacing(5)

        self.btn_title = QPushButton("🏷️")
        self.btn_title.setFixedSize(40, 40)
        self.btn_title.setToolTip("Convertir en TITLE")
        self.btn_title.clicked.connect(lambda: self.set_row_type("TITLE"))

        self.btn_product = QPushButton("📦")
        self.btn_product.setFixedSize(40, 40)
        self.btn_product.setToolTip("Convertir en PRODUCT")
        self.btn_product.clicked.connect(lambda: self.set_row_type("PRODUCT"))

        self.btn_info = QPushButton("ℹ️")
        self.btn_info.setFixedSize(40, 40)
        self.btn_info.setToolTip("Convertir en INFO")
        self.btn_info.clicked.connect(lambda: self.set_row_type("INFO"))

        self.btn_empty = QPushButton("⬜")
        self.btn_empty.setFixedSize(40, 40)
        self.btn_empty.setToolTip("Convertir en EMPTY")
        self.btn_empty.clicked.connect(lambda: self.set_row_type("EMPTY"))

        type_grid.addWidget(self.btn_title, 0, 0)
        type_grid.addWidget(self.btn_product, 0, 1)
        type_grid.addWidget(self.btn_info, 1, 0)
        type_grid.addWidget(self.btn_empty, 1, 1)

        sidebar_layout.addLayout(type_grid)

        self.row_type_buttons = {
            "TITLE": self.btn_title,
            "PRODUCT": self.btn_product,
            "INFO": self.btn_info,
            "EMPTY": self.btn_empty,
        }

        # Separador flexible
        sidebar_layout.addStretch()

        # --- Botones globales ---
        self.listen_button = QPushButton("🎙️")
        self.listen_button.setFixedSize(40, 40)
        self.listen_button.setToolTip("🎙️")
        self.listen_button.clicked.connect(self.listen_voice)
        sidebar_layout.addWidget(self.listen_button, alignment=Qt.AlignHCenter)

        self.excel_button = QPushButton("💾")
        self.excel_button.setFixedSize(40, 40)
        self.excel_button.setToolTip("Exportar a Excel")
        self.excel_button.clicked.connect(self.export_excel)
        sidebar_layout.addWidget(self.excel_button, alignment=Qt.AlignHCenter)

        # --------------------------------------------------
        # Tabla
        # --------------------------------------------------


        self.HIGHLIGHT_COLORS = {
            "PRODUCT": QColor(255, 230, 160),
            "INFO":    QColor(230, 230, 200),
            "TITLE":   QColor(220, 220, 220),
            "EMPTY":   QColor(210, 210, 210),
        }
        self.table = QTableWidget(self.model.row_count(), 5)
        self.table.setHorizontalHeaderLabels(
            ["KITS", "PRODUCTO", "CANTIDAD", "PRECIO", "TOTAL"]
        )
        self._init_table_items()
        self.table.cellChanged.connect(self.on_cell_changed)
        self.table.cellClicked.connect(self.on_cell_clicked)

        # --------------------------------------------------
        # Lista de productos
        # --------------------------------------------------
        self.product_list = QListWidget()
        self.product_list.setMaximumWidth(350)
        self.product_list.itemClicked.connect(self.on_product_clicked)
        self.product_list.hide()

        # --------------------------------------------------
        # Input comandos
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
        row_count = self.model.row_count()
        if row_count == 0:
            return  # nada que hacer

        INFO_BG = QColor(250, 245, 230)
        ACTIVE_INFO_BG = QColor(255, 255, 0, 100)

        self.update_row_type_buttons()
        for r in range(self.table.rowCount()):
            if r >= row_count:
                continue  # evitar pedir filas que no existen

            row = self.model.get_row(r)
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if not item:
                    continue

                if r == self.active_row:
                    # ACTIVE overrides, depende del tipo
                    if row.type == "TITLE":
                        item.setBackground(QColor(180, 200, 255))  # azul + highlight
                    elif row.type == "INFO":
                        item.setBackground(QColor(255, 255, 150))
                    elif row.type == "EMPTY":
                        item.setBackground(QColor(230, 230, 180))
                    else:  # PRODUCT
                        item.setBackground(ACTIVE_INFO_BG)
                    item.setForeground(Qt.black)
                else:
                    # colores normales
                    if row.type == "TITLE":
                        item.setBackground(Qt.blue)
                        item.setForeground(Qt.white)
                    elif row.type == "INFO":
                        item.setBackground(INFO_BG)
                        item.setForeground(Qt.black)
                    elif row.type == "EMPTY":
                        item.setBackground(Qt.lightGray)
                        item.setForeground(Qt.black)
                    else:
                        item.setBackground(Qt.white)
                        item.setForeground(Qt.black)



    def on_cell_clicked(self, row, column):
        self.active_row = row
        self.state.active_row = row

        row_type = self.model.get_row(row).type

        # Solo PRODUCT + columna PRODUCTO
        if row_type == "PRODUCT" and column == 1:
            self.state.mode = CommandMode.PRODUCT
            self.state.product_buffer.clear()
            self.state.product_matches = list(self.materials.keys())
        else:
            self.state.mode = CommandMode.IDLE

        self.highlight_active_row()
        self.highlight_active_cell()
        self.update_product_suggestions()



    def refresh_row(self, row_index):
        """
        Actualiza la UI de la fila a partir del modelo sin entrar en bucles infinitos.
        TITLE/INFO respetan manual edits en columnas 0–2.
        """
        row = self.model.get_row(row_index)

        self.table.blockSignals(True)  # 🔹 bloquear señales

        for col_index in range(5):
            current_text = row.as_list()[col_index]

            # TITLE/INFO: respetar manual edits en columnas 0–2
            if row.type in ("TITLE", "INFO") and col_index < 3:
                # Solo actualizar si la celda está vacía
                item = self.table.item(row_index, col_index)
                if item is None:
                    item = QTableWidgetItem(current_text)
                    self.table.setItem(row_index, col_index, item)
                continue

            # PRODUCT/EMPTY: siempre reflejar modelo
            item = self.table.item(row_index, col_index)
            if item is None:
                item = QTableWidgetItem(current_text)
                self.table.setItem(row_index, col_index, item)
            else:
                item.setText(current_text)

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
        proforma_row = self.model.get_row(row)
        item = self.table.item(row, column)
        if not item:
            return

        text = item.text() or ""

        # Actualizar modelo **directamente**
        if column == 0:
            proforma_row.col_0 = text
        elif column == 1:
            proforma_row.col_1 = text
        elif column == 2:
            proforma_row.col_2 = text
        elif column == 3:
            proforma_row.col_3 = text
        elif column == 4:
            proforma_row.col_4 = text


        # Solo recalcular TOTAL si es PRODUCT
        if proforma_row.type == "PRODUCT":
            try:
                qty = float(proforma_row.col_2)
            except (ValueError, TypeError):
                qty = 0
            try:
                price = float(proforma_row.col_3)
            except (ValueError, TypeError):
                price = 0
            proforma_row.col_4 = str(round(qty * price, 2)) if qty * price != 0 else ""

        # 🔹 NO refrescar TITLE/INFO columnas 0–2 para evitar sobrescribir edits
        if proforma_row.type in ("TITLE", "INFO"):
            self.refresh_row(row_index=row)  # se respeta manual edit
        else:
            self.refresh_row(row_index=row)




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
            self.listen_button.setText("⏹️")
            grammar = build_grammar(self.materials)
            self.voice_worker = VoiceListener(grammar=grammar)
            self.voice_worker.result_ready.connect(self.on_voice_result)
            self.voice_worker.start()
        else:
            self.listening = False
            self.listen_button.setText("🎙️")
            if self.voice_worker:
                self.voice_worker.stop()
                self.voice_worker = None

    def on_voice_result(self, text):
        normalized = normalize_command(text)
        self._process_tokens(normalized.split())
        self.refresh_all_rows()

    def _process_tokens(self, tokens):
        repeat_allowed = ["SIGUIENTE", "NUEVA", "PRODUCTO", "KIT", "EPOXI",
                        "UNO", "DOS", "TRES", "CUATRO", "CINCO", "SEIS",
                        "SIETE", "OCHO", "NUEVE", "CERO"]

        for token in tokens:
            if token == self.last_token and token not in repeat_allowed:
                continue
            self.last_token = token

            before_rows = self.model.row_count()

            msg = self.state.handle_word(token, self.model)

            after_rows = self.model.row_count()

            # 🔹 Actualizar active_row desde CommandState
            self.active_row = min(self.state.active_row, after_rows - 1) if after_rows > 0 else 0

            self.status_label.setText(msg)

            # 🔴 Sincronizar filas de tabla con el modelo
            if after_rows != before_rows:
                # Asegurarnos de eliminar filas sobrantes si se borraron
                self.table.setRowCount(after_rows)
                self.refresh_all_rows()
            else:
                # Solo refrescar la fila activa
                if 0 <= self.active_row < after_rows:
                    self.refresh_row(self.active_row)

            # 🔹 Highlight siempre sobre fila activa válida
            if after_rows > 0:
                self.highlight_active_row()
                self.highlight_active_cell()

            # 🔹 Actualizar sugerencias de producto
            self.update_product_suggestions()


    # ======================================================
    # ProductBuffer UI
    # ======================================================

    def update_product_suggestions(self):
        self.product_list.clear()
        if self.state.mode != CommandMode.PRODUCT:
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
        if self.state.mode == CommandMode.QUANTITY:
            col = 2
        elif self.state.mode == CommandMode.PRICE:
            col = 3
        else:
            return

        item = self.table.item(self.active_row, col)
        if item:
            item.setBackground(Qt.cyan)

    def create_dummy_starting_rows(self):
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

    def delete_current_row(self):
        if self.model.row_count() == 0:
            return

        row = self.active_row

        # Borrar del modelo
        self.model.remove_row(row)

        # Ajustar fila activa
        if self.active_row >= self.model.row_count():
            self.active_row = self.model.row_count() - 1

        # 🔹 Refrescar tabla completa
        self.table.setRowCount(self.model.row_count())
        self._init_table_items()           # asegura que todos los QTableWidgetItem existen
        self.refresh_all_rows()
        self.highlight_active_row()


        
    def set_row_type(self, new_type: str):
        if self.active_row < 0 or self.active_row >= self.model.row_count():
            return

        row = self.model.get_row(self.active_row)

        # Si ya es de ese tipo, no hacemos nada
        if row.type == new_type:
            return

        # Resetear contenido según tipo
        if new_type == "TITLE":
            self.model.rows[self.active_row] = ProformaRow(type="TITLE", col_1=row.col_1 or "")
        elif new_type == "PRODUCT":
            self.model.rows[self.active_row] = ProformaRow(type="PRODUCT")
        elif new_type == "INFO":
            self.model.rows[self.active_row] = ProformaRow(type="INFO")
        elif new_type == "EMPTY":
            self.model.rows[self.active_row] = ProformaRow(type="EMPTY")

        # Refrescar UI
        self.refresh_row(self.active_row)
        self.highlight_active_row()

    def update_row_type_buttons(self):
        current_type = self.model.get_row(self.active_row).type

        for row_type, button in self.row_type_buttons.items():
            if row_type == current_type:
                button.setStyleSheet(
                    "background-color: #ffd966; font-weight: bold;"
                )
            else:
                button.setStyleSheet("")
