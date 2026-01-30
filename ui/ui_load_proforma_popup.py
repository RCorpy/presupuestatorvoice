from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt
from db.proformas_repository import search_proformas, load_proforma_rows
from excel.excel_exporter import export_proforma_to_excel
from db.proformas_repository import get_proforma_full_data
import sqlite3


class LoadProformaPopup(QDialog):

    def __init__(self, parent=None, proforma_model=None):
        super().__init__(parent)
        self.proforma_model = proforma_model

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

        # 🟥 IZQUIERDA → cancelar
        left_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        left_layout.addWidget(cancel_btn)

        # 🟨 CENTRO → exportar
        center_layout = QHBoxLayout()
        excel_btn = QPushButton("Exportar a Excel")
        center_layout.addWidget(excel_btn)

        # 🟩 DERECHA → cargar
        right_layout = QHBoxLayout()
        load_btn = QPushButton("Cargar proforma")
        right_layout.addWidget(load_btn)

        # Espacios entre zonas
        btn_row.addLayout(left_layout)
        btn_row.addStretch()
        btn_row.addLayout(center_layout)
        btn_row.addStretch()
        btn_row.addLayout(right_layout)

        main_layout.addLayout(btn_row)


        # ==========================
        # CONEXIONES
        # ==========================
        cancel_btn.clicked.connect(self.reject)
        load_btn.clicked.connect(self.on_load)
        excel_btn.clicked.connect(self.on_export_excel)


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

    def on_export_excel(self):
        if not self.selected_proforma:
            QMessageBox.warning(
                self,
                "Selecciona una proforma",
                "Debes seleccionar una proforma primero."
            )
            return

        if not self.proforma_model:
            return

        # 🔹 Cargar filas
        rows = load_proforma_rows(self.selected_proforma)
        self.proforma_model.clear()
        for row in rows:
            self.proforma_model.add_row(row)

        # 🔹 Cargar datos generales


        data = get_proforma_full_data(self.selected_proforma)
        if data:
            (
                pid,
                area_m2,
                color,
                created_at,
                discount,
                shipping,
                name,
                phone,
                email,
                address,
                city,
                province,
                cp,
                cif
            ) = data

            self.proforma_model.proforma_id = pid
            self.proforma_model.area_m2 = area_m2
            self.proforma_model.main_color = color
            self.proforma_model.created_at = created_at
            self.proforma_model.discount_percent = discount
            self.proforma_model.shipping_cost = shipping

            self.proforma_model.client_name = name
            self.proforma_model.phone = phone
            self.proforma_model.email = email
            self.proforma_model.address = address
            self.proforma_model.city = city
            self.proforma_model.province = province
            self.proforma_model.postal_code = cp
            self.proforma_model.cif = cif

        try:
            export_proforma_to_excel(self.proforma_model)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo exportar el Excel:\n{e}"
            )

