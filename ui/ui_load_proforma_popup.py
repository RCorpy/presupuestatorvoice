from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QGroupBox, QMessageBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from db.proformas_repository import search_proformas, load_proforma_rows
import sqlite3


class LoadProformaPopup(QDialog):

    def __init__(self, parent=None, proforma_model=None):
        super().__init__(parent)
        self.proforma_model = proforma_model
        base_font = QFont()
        base_font.setPointSize(18)
        self.setFont(base_font)

        self.setWindowTitle("Cargar proforma")
        self.setMinimumSize(900, 600)

        self.selected_proforma = None

        main_layout = QVBoxLayout(self)

        # ==========================
        # BUSCADOR
        # ==========================
        search_row = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o teléfono")

        search_row.addWidget(QLabel("Buscar"))
        search_row.addWidget(self.search_input)

        main_layout.addLayout(search_row)

        # ==========================
        # CUERPO
        # ==========================
        body = QHBoxLayout()

        # ---- LISTA ----
        self.list_widget = QListWidget()
        body.addWidget(self.list_widget, 2)

        # ---- PREVIEW ----
        preview_box = QGroupBox("Vista previa")
        preview_layout = QVBoxLayout()

        self.lbl_client = QLabel("-")
        self.lbl_phone = QLabel("-")
        self.lbl_area = QLabel("-")
        self.lbl_color = QLabel("-")
        self.lbl_date = QLabel("-")
        self.lbl_total = QLabel("-")

        preview_layout.addWidget(QLabel("Cliente:"))
        preview_layout.addWidget(self.lbl_client)

        preview_layout.addWidget(QLabel("Teléfono:"))
        preview_layout.addWidget(self.lbl_phone)

        preview_layout.addWidget(QLabel("Superficie:"))
        preview_layout.addWidget(self.lbl_area)

        preview_layout.addWidget(QLabel("Color:"))
        preview_layout.addWidget(self.lbl_color)

        preview_layout.addWidget(QLabel("Fecha:"))
        preview_layout.addWidget(self.lbl_date)

        preview_layout.addWidget(QLabel("Total:"))
        preview_layout.addWidget(self.lbl_total)


        preview_box.setLayout(preview_layout)
        body.addWidget(preview_box, 1)

        main_layout.addLayout(body)

        # ==========================
        # BOTONES
        # ==========================
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancelar")
        load_btn = QPushButton("Cargar proforma")

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(load_btn)

        main_layout.addLayout(btn_row)

        # ==========================
        # CONEXIONES
        # ==========================
        cancel_btn.clicked.connect(self.reject)
        load_btn.clicked.connect(self.on_load)

        self.search_input.textChanged.connect(self.update_list)
        self.list_widget.itemClicked.connect(self.on_item_selected)

        self.update_list()

    # ==========================
    # DATA
    # ==========================
    def update_list(self):
        text = self.search_input.text().strip()
        self.list_widget.clear()

        try:
            proformas = search_proformas(text)  # devuelve lista de tuplas: id, name, phone, area_m2, main_color, created_at
        except Exception:
            proformas = []  # fallback vacío

        for p in proformas:
            proforma_id, name, phone, area_m2, color, created_at = p
            label = f"{created_at[:10]} — {name} — {area_m2} m² — {color}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, proforma_id)  # guardamos solo el ID
            self.list_widget.addItem(item)


    def on_item_selected(self, item):
        proforma_id = item.data(Qt.UserRole)
        self.selected_proforma = proforma_id

        from db.proformas_repository import get_proforma_preview

        row = get_proforma_preview(proforma_id)

        if row:
            name, phone, area_m2, color, created_at = row
            self.lbl_client.setText(name)
            self.lbl_phone.setText(phone)
            self.lbl_area.setText(f"{area_m2} m²")
            self.lbl_color.setText(color)
            self.lbl_date.setText(created_at[:10])

        rows = load_proforma_rows(proforma_id)
        total = self._calculate_total_from_rows(rows)
        self.lbl_total.setText(f"{total:.2f} €")



    def on_load(self):
        if not self.selected_proforma:
            QMessageBox.warning(
                self,
                "Selecciona una proforma",
                "Debes seleccionar una proforma primero."
            )
            return

        if self.proforma_model:
            rows = load_proforma_rows(self.selected_proforma)
            print("rows", rows)
            self.proforma_model.clear()
            for row in rows:
                self.proforma_model.add_row(row)

        self.accept()


    # ==========================
    # MOCK
    # ==========================
    def _mock_proformas(self, text):
        dummy = [
            {
                "id": 1,
                "client_name": "Juan Pérez",
                "phone": "612345678",
                "area_m2": 25,
                "color": "Blanco",
                "date": "12/01/2026",
                "state": {},
            },
            {
                "id": 2,
                "client_name": "Ana López",
                "phone": "699112233",
                "area_m2": 40,
                "color": "Gris",
                "date": "03/12/2025",
                "state": {},
            },
        ]

        if not text:
            return dummy

        return [
            p for p in dummy
            if text in p["client_name"].lower()
            or text in p["phone"]
        ]

    def _calculate_total_from_rows(self, rows):
        total = 0.0
        for row in rows:
            if row.type != "PRODUCT":
                continue
            try:
                qty = float(row.col_2 or 0)
                price = float(row.col_3 or 0)
                total += qty * price
            except ValueError:
                pass
        return total
