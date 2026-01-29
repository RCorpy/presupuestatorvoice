from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QGroupBox, QMessageBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class LoadProformaPopup(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

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
        text = self.search_input.text().strip().lower()
        self.list_widget.clear()

        try:
            from db.proformas_repository import get_proformas_matches
            proformas = get_proformas_matches(text)

        except Exception:
            proformas = self._mock_proformas(text)

        for p in proformas:
            label = f"{p['client_name']} — {p['area_m2']} m² — {p['color']}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, p)
            self.list_widget.addItem(item)

    def on_item_selected(self, item):
        proforma = item.data(Qt.UserRole)
        self.selected_proforma = proforma

        self.lbl_client.setText(proforma["client_name"])
        self.lbl_phone.setText(proforma["phone"])
        self.lbl_area.setText(f"{proforma['area_m2']} m²")
        self.lbl_color.setText(proforma["color"])
        self.lbl_date.setText(proforma["date"])

    def on_load(self):
        if not self.selected_proforma:
            QMessageBox.warning(
                self,
                "Selecciona una proforma",
                "Debes seleccionar una proforma primero."
            )
            return

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
