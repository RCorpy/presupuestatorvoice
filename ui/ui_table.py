# ui/ui_table.py

from PySide6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QWidget, QGridLayout,
    QLineEdit, QLabel, QPushButton, QListWidget, QStyledItemDelegate
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
        self._updating_ui = False
        self.user_editing = False


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
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.setItemDelegate(UserEditDelegate(self))


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
        #self.create_dummy_starting_rows()
        self.table.setRowCount(self.model.row_count())
        self._init_table_items()
        self.refresh_all_rows()
        self.highlight_active_row()


        self.table.setColumnWidth(0, 200)  # suficiente para mostrar info
        self.table.setColumnWidth(1, 250)  # producto
        self.table.setColumnWidth(2, 70)   # cantidad
        self.table.setColumnWidth(3, 70)   # precio
        self.table.setColumnWidth(4, 70)   # total




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
        self._updating_ui = True
        self.table.blockSignals(True)

        for col_index in range(5):
            current_text = row.as_list()[col_index]
            # 🔹 Obtener o crear el item siempre
            item = self.table.item(row_index, col_index)
            if item is None:
                item = QTableWidgetItem()
                self.table.setItem(row_index, col_index, item)

            # ⚡ Asegurarse de que la celda esté habilitada
            item.setFlags(item.flags() | Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            # Actualizar texto
            item.setText(current_text)

            # Mensaje de debug
            #if row.type in ("TITLE", "INFO") and col_index < 2:
            #    print("REFRESH", row.type, col_index, current_text)

        self.table.blockSignals(False)
        self._updating_ui = False



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
        if self._updating_ui:
            return
        if not self.user_editing:
            return
        item = self.table.item(row, column)
        if not item:
            return

        text = item.text() or ""
        proforma_row = self.model.get_row(row)

        # 🔒 Si el valor ya es el mismo, NO hacer nada
        current = [
            proforma_row.col_0,
            proforma_row.col_1,
            proforma_row.col_2,
            proforma_row.col_3,
            proforma_row.col_4,
        ][column]

        if text == current:
            return

        # ✅ UI → MODELO (única dirección permitida aquí)
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

        # 🔢 Recalcular TOTAL solo si toca
        if proforma_row.type == "PRODUCT" and column in (2, 3):
            try:
                qty = float(proforma_row.col_2)
                price = float(proforma_row.col_3)
                proforma_row.col_4 = str(round(qty * price, 2))
            except:
                proforma_row.col_4 = ""
        if proforma_row.type == "PRODUCT" and column in (2, 3):
            self._updating_ui = True
            total_item = self.table.item(row, 4)
            if total_item:
                total_item.setText(proforma_row.col_4)
            self._updating_ui = False


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
        self.model.add_row(ProformaRow(
            type="TITLE", 
            col_0="KIT EPOXI", 
            col_1="2 CAPAS EPOXI VERDE"
        ))
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
            col_0="CATALIZADOR 5:1",
            col_1="100% SÓLIDOS",
            col_2="test"
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

        old_row = self.model.get_row(self.active_row)

        if old_row.type == new_type:
            return

        if new_type == "TITLE":
            new_row = ProformaRow(
                type="TITLE",
                col_0=old_row.col_0,
                col_1=old_row.col_1
            )

        elif new_type == "PRODUCT":
            new_row = ProformaRow(type="PRODUCT")

        elif new_type == "INFO":
            new_row = ProformaRow(
                type="INFO",
                col_0=old_row.col_0,
                col_1=old_row.col_1,
                col_2=old_row.col_2,
                col_3=old_row.col_3,
                col_4=old_row.col_4,
            )

        elif new_type == "EMPTY":
            new_row = ProformaRow(type="EMPTY")

        else:
            return  # seguridad

        self.model.set_row(self.active_row, new_row)
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

    def _on_selection_changed(self):
        self.user_editing = False

    def refresh_row_except(self, row_index, except_column):
        row = self.model.get_row(row_index)
        self._updating_ui = True
        self.table.blockSignals(True)

        values = row.as_list()
        for col in range(5):
            if col == except_column:
                continue  # ⚠️ NO tocar la celda editada

            item = self.table.item(row_index, col)
            if not item:
                item = QTableWidgetItem()
                self.table.setItem(row_index, col, item)

            item.setText(values[col])

        self.table.blockSignals(False)
        self._updating_ui = False

class UserEditDelegate(QStyledItemDelegate):
    def __init__(self, table):
        super().__init__(table)
        self.table = table

    def createEditor(self, parent, option, index):
        self.table.user_editing = True
        return super().createEditor(parent, option, index)

    def destroyEditor(self, editor, index):
        self.table.user_editing = False
        super().destroyEditor(editor, index)



