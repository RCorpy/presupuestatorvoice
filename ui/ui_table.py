from PySide6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QLineEdit, QLabel, QPushButton, QFileDialog
)
from PySide6.QtCore import Qt
from voice.voice_listener import VoiceListener
from voice.voice_normalizer import normalize_command
from commands.command_state import CommandState
from excel.excel_exporter import export_proforma_to_excel
from model import ProformaModel
from db.materials_repository import load_materials
from voice.grammar_builder import build_grammar



class ProformaTableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor de Proforma")
        self.resize(700, 400)
        self.materials = load_materials()

        self.model = ProformaModel(rows=5)
        self.state = CommandState(self.materials)
        self.active_row = 0
        self.listening = False
        self.voice_worker = None
        self.last_token = None
        

        # Tabla
        self.table = QTableWidget(self.model.row_count(), 4)
        self.table.setHorizontalHeaderLabels(["PRODUCTO", "CANTIDAD", "PRECIO", "TOTAL"])
        self._init_table_items()
        self.table.cellChanged.connect(self.on_cell_changed)

        # Input de comando
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Escribe un comando: FILA 2 CONSULTORIA CANTIDAD 3")
        self.command_input.returnPressed.connect(self.process_command)

        # Botón de voz
        self.listen_button = QPushButton("🎙️ Escuchar")
        self.listen_button.clicked.connect(self.listen_voice)

        #Boton de guardado excel
        self.excel_button = QPushButton("💾 Exportar a Excel")
        self.excel_button.clicked.connect(self.export_excel)



        # Label de estado
        self.status_label = QLabel(f"Fila activa: {self.active_row + 1}")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.status_label)
        layout.addWidget(self.command_input)
        layout.addWidget(self.listen_button)
        layout.addWidget(self.excel_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.refresh_all_rows()
        self.highlight_active_row()

    def _init_table_items(self):
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item is None:
                    item = QTableWidgetItem("")
                    if c == 3:
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(r, c, item)

    def highlight_active_row(self):
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if not item:
                    item = QTableWidgetItem("")
                    self.table.setItem(r, c, item)
                item.setBackground(Qt.yellow if r == self.active_row else Qt.white)

    def on_cell_changed(self, row, column):
        if column == 0:
            self.model.set_producto(row, self.table.item(row, column).text())
        elif column == 1:
            try:
                self.model.set_cantidad(row, int(self.table.item(row, column).text()))
            except ValueError:
                pass
        elif column == 2:
            try:
                self.model.set_precio(row, float(self.table.item(row, column).text()))
            except ValueError:
                pass
        self.refresh_row(row)

    def refresh_row(self, row):
        row_data = self.model.data[row]
        for col, key in enumerate(["producto", "cantidad", "precio", "total"]):
            item = self.table.item(row, col)
            if item is None:
                item = QTableWidgetItem("")
                if col == 3:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)

            value = row_data[key]
            if key == "total":
                item.setText(f"{value:.2f}" if value != "" else "")
            else:
                item.setText(str(value))

    def refresh_all_rows(self):
        for r in range(self.model.row_count()):
            self.refresh_row(r)

    def sync_table_rows(self):
        rows_needed = self.model.row_count()
        if rows_needed > self.table.rowCount():
            self.table.setRowCount(rows_needed)
            self._init_table_items()

    def process_command(self):
        command_text = self.command_input.text().upper()
        self.command_input.clear()
        self._process_tokens(command_text.split())

    def listen_voice(self):
        if not self.listening:
            self.listen_button.setText("⏹️ Parar")
            self.status_label.setText("🎙️ Micrófono activado")
            self.listening = True
            
            grammar = build_grammar(self.materials)
            self.voice_worker = VoiceListener(grammar=grammar)
            
            self.voice_worker.result_ready.connect(self.on_voice_result)
            self.voice_worker.start()
        else:
            self.listen_button.setText("🎙️ Escuchar")
            self.status_label.setText("🎙️ Micrófono desactivado")
            self.listening = False
            if self.voice_worker:
                self.voice_worker.stop()
                self.voice_worker = None

    def on_voice_result(self, text):
        normalized = normalize_command(text)
        self._process_tokens(normalized.split())

    

    def _process_tokens(self, tokens):
        print(tokens)

        repeat_allowed = ["SIGUIENTE", "NUEVA"]

        for token in tokens:
            if token == self.last_token and token not in repeat_allowed:
                continue
            self.last_token = token

            msg = self.state.handle_word(token, self.model)
            self.active_row = self.state.active_row  # sincroniza fila activa
            self.status_label.setText(msg)

            # Sincronizar UI
            self.sync_table_rows()
            self.refresh_row(self.active_row)
            self.highlight_active_row()

    def export_excel(self):
        try:
            path = export_proforma_to_excel(self.model)
            self.status_label.setText(f"Excel creado: {path}")
        except Exception as e:
            self.status_label.setText(f"Error exportando Excel: {e}")

