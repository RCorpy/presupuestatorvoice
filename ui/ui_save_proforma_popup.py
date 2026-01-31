from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QLabel, QPushButton,
    QGroupBox, QListWidget, QListWidgetItem, QDateEdit, QMessageBox
)
from PySide6.QtCore import QDate

from db.clients_repository import get_matches, create_or_update_client, client_exists
from db.proformas_repository import create_proforma
from excel.excel_exporter import export_proforma_to_excel
from datetime import datetime

class SaveProformaPopup(QDialog):

    def __init__(self, parent, proforma_model, ui_data):
        super().__init__(parent)

        self.proforma_model = proforma_model
        self.ui_data = ui_data

        self.setWindowTitle("Guardar proforma")
        self.setMinimumSize(1250, 800)

        main_layout = QHBoxLayout(self)

        # ==========================
        # COLUMNA IZQUIERDA
        # ==========================
        left_col = QVBoxLayout()

        # -------- CLIENTE --------
        client_box = QGroupBox("Datos del cliente")
        client_form = QFormLayout()

        self.name_input = QLineEdit(ui_data.get("customer_name", ""))
        self.phone_input = QLineEdit(ui_data.get("customer_phone", ""))
        self.email_input = QLineEdit()
        self.cif_input = QLineEdit()
        self.address_input = QLineEdit()
        self.cp_input = QLineEdit()
        self.city_input = QLineEdit()
        self.province_input = QLineEdit()

        client_form.addRow("Nombre", self.name_input)
        client_form.addRow("Teléfono", self.phone_input)
        client_form.addRow("Email", self.email_input)
        client_form.addRow("CIF / NIF", self.cif_input)
        client_form.addRow("Dirección fiscal", self.address_input)

        row = QHBoxLayout()
        row.addWidget(QLabel("CP"))
        row.addWidget(self.cp_input)
        row.addWidget(QLabel("Ciudad"))
        row.addWidget(self.city_input)
        row.addWidget(QLabel("Provincia"))
        row.addWidget(self.province_input)
        client_form.addRow(row)

        client_box.setLayout(client_form)
        left_col.addWidget(client_box)

        # -------- PROFORMA --------
        proforma_box = QGroupBox("Datos de la proforma")
        proforma_form = QFormLayout()

        self.area_input = QLineEdit(str(ui_data.get("area_m2", "")))
        self.area_input.setReadOnly(True)

        self.color_input = QLineEdit(ui_data.get("color", ""))
        self.color_input.setReadOnly(True)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)

        proforma_form.addRow("Superficie (m²)", self.area_input)
        proforma_form.addRow("Color principal", self.color_input)
        proforma_form.addRow("Fecha", self.date_input)

        proforma_box.setLayout(proforma_form)
        left_col.addWidget(proforma_box)

        # -------- ENVÍO --------
        ship_box = QGroupBox("Datos de envío (opcional)")
        ship_form = QFormLayout()

        self.ship_address = QLineEdit()
        self.ship_cp = QLineEdit()
        self.ship_city = QLineEdit()
        self.ship_province = QLineEdit()
        self.ship_contact = QLineEdit()
        self.ship_phone = QLineEdit()
        self.ship_notes = QTextEdit()

        ship_form.addRow("Dirección envío", self.ship_address)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("CP"))
        row2.addWidget(self.ship_cp)
        row2.addWidget(QLabel("Ciudad"))
        row2.addWidget(self.ship_city)
        row2.addWidget(QLabel("Provincia"))
        row2.addWidget(self.ship_province)
        ship_form.addRow(row2)

        ship_form.addRow("Contacto", self.ship_contact)
        ship_form.addRow("Teléfono", self.ship_phone)
        ship_form.addRow("Observaciones", self.ship_notes)

        ship_box.setLayout(ship_form)
        left_col.addWidget(ship_box)

        main_layout.addLayout(left_col, 3)

        # ==========================
        # COLUMNA DERECHA – MATCHES
        # ==========================
        right_col = QVBoxLayout()

        right_col.addWidget(QLabel("Clientes existentes"))

        self.matches_list = QListWidget()
        right_col.addWidget(self.matches_list)

        main_layout.addLayout(right_col, 1)

        # ==========================
        # BOTONES
        # ==========================
        btn_row = QHBoxLayout()

        # 🟥 IZQUIERDA → cancelar
        left_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        left_layout.addWidget(cancel_btn)

        # 🟨 CENTRO → guardar + excel
        center_layout = QHBoxLayout()
        save_excel_btn = QPushButton("Guardar y exportar Excel")
        center_layout.addWidget(save_excel_btn)

        # 🟩 DERECHA → guardar
        right_layout = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        right_layout.addWidget(save_btn)

        btn_row.addLayout(left_layout)
        btn_row.addStretch()
        btn_row.addLayout(center_layout)
        btn_row.addStretch()
        btn_row.addLayout(right_layout)

        left_col.addLayout(btn_row)


        # ==========================
        # CONEXIONES (búsqueda)
        # ==========================
        self.phone_input.textChanged.connect(self.update_matches)
        self.name_input.textChanged.connect(self.update_matches)

        self.matches_list.itemClicked.connect(self.apply_client_match)

        save_btn.clicked.connect(self.on_save)
        save_excel_btn.clicked.connect(self.on_save_and_export)
        cancel_btn.clicked.connect(self.reject)



        self.update_matches()


    
    def update_matches(self):
        """
        Actualiza la lista de clientes coincidentes.
        Prioridad:
        1) Teléfono
        2) Nombre
        """
        phone = self.phone_input.text().strip()
        name = self.name_input.text().strip()

        self.matches_list.clear()

        try:
            matches = get_matches(phone, name)
        except Exception:
            matches = self._mock_client_search(phone, name)


        for client in matches:
            label = f"{client['name']} — {client['phone']}"
            item = QListWidgetItem(label)
            item.setData(1, client)  # guardamos el dict entero
            self.matches_list.addItem(item)

    def _mock_client_search(self, phone, name):
        """
        Mock temporal para probar la UI.
        Será sustituido por clients_repository.get_matches(...)
        """
        dummy_clients = [
            {
                "name": "Juan Pérez",
                "phone": "612345678",
                "email": "juan@test.com",
                "cif": "12345678A",
                "address": "Calle Mayor 1",
                "cp": "28001",
                "city": "Madrid",
                "province": "Madrid",
            },
            {
                "name": "Ana López",
                "phone": "699112233",
                "email": "ana@test.com",
                "cif": "87654321B",
                "address": "Av. Sol 3",
                "cp": "08001",
                "city": "Barcelona",
                "province": "Barcelona",
            },
        ]

        if phone:
            return [c for c in dummy_clients if phone in c["phone"]]

        return [c for c in dummy_clients if name.lower() in c["name"].lower()]

    def apply_client_match(self, item):
        client = item.data(1)
        if not client:
            return

        self.name_input.setText(client.get("name", ""))
        self.phone_input.setText(client.get("phone", ""))
        self.email_input.setText(client.get("email", ""))
        self.cif_input.setText(client.get("cif", ""))
        self.address_input.setText(client.get("address", ""))
        self.cp_input.setText(client.get("cp", ""))
        self.city_input.setText(client.get("city", ""))
        self.province_input.setText(client.get("province", ""))

    def on_save(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()

        if not name or not phone:
            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Nombre y teléfono son obligatorios."
            )
            return False

        # -------- CLIENTE FISCAL --------
        client_data = {
            "name": name,
            "phone": phone,
            "email": self.email_input.text().strip(),
            "cif": self.cif_input.text().strip(),
            "address": self.address_input.text().strip(),
            "cp": self.cp_input.text().strip(),
            "city": self.city_input.text().strip(),
            "province": self.province_input.text().strip(),
        }

        client_id = create_or_update_client(client_data)

        # -------- ENVÍO (opcional) --------
        shipping_data = {
            "address": self.ship_address.text().strip(),
            "cp": self.ship_cp.text().strip(),
            "city": self.ship_city.text().strip(),
            "province": self.ship_province.text().strip(),
            "contact": self.ship_contact.text().strip(),
            "phone": self.ship_phone.text().strip(),
            "notes": self.ship_notes.toPlainText().strip(),
        }

        if not any(shipping_data.values()):
            shipping_data = None

        # -------- PROFORMA --------
        proforma_id = create_proforma(
            client_id=client_id,
            area_m2=self.ui_data["area_m2"],
            main_color=self.ui_data["color"],
            discount_percent=self.ui_data.get("discount_percent", 0),
            shipping_cost=self.ui_data.get("shipping_cost", 0),
            table_rows=self.proforma_model.rows,
            shipping_data=shipping_data,
            notes=None
        )

        QMessageBox.information(
            self,
            "Guardado",
            f"Proforma guardada correctamente (ID {proforma_id})"
        )

        return True

    def on_save_and_export(self):
        is_saved = self.on_save()
        if not is_saved:
            return

        # ==========================
        # DATOS CLIENTE (flat, compatibles con exporter)
        # ==========================
        self.proforma_model.client_name = self.name_input.text().strip()
        self.proforma_model.phone = self.phone_input.text().strip()
        self.proforma_model.email = self.email_input.text().strip()
        self.proforma_model.cif = self.cif_input.text().strip()
        self.proforma_model.address = self.address_input.text().strip()
        self.proforma_model.postal_code = self.cp_input.text().strip()
        self.proforma_model.city = self.city_input.text().strip()
        self.proforma_model.province = self.province_input.text().strip()

        # ==========================
        # DATOS PROFORMA
        # ==========================
        self.proforma_model.area_m2 = self.ui_data.get("area_m2", "")
        self.proforma_model.main_color = self.ui_data.get("color", "")
        self.proforma_model.discount_percent = self.ui_data.get("discount_percent", 0)
        self.proforma_model.shipping_cost = self.ui_data.get("shipping_cost", 0)

        self.proforma_model.shipping_contact = self.ship_contact.text().strip()
        self.proforma_model.shipping_address = self.ship_address.text().strip()
        self.proforma_model.shipping_postal_code = self.ship_cp.text().strip()
        self.proforma_model.shipping_city = self.ship_city.text().strip()
        self.proforma_model.shipping_province = self.ship_province.text().strip()
        self.proforma_model.shipping_phone = self.ship_phone.text().strip()
        self.proforma_model.shipping_notes = self.ship_notes.toPlainText().strip()

        # ⚠️ MUY IMPORTANTE: formato fecha correcto
        self.proforma_model.created_at = datetime.now().strftime("%Y-%m-%d")

        # opcional: si más adelante expones el ID
        self.proforma_model.proforma_id = ""

        # ==========================
        # EXPORT
        # ==========================
        try:
            export_proforma_to_excel(self.proforma_model)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Proforma guardada",
                f"La proforma se guardó, pero el Excel falló:\n{e}"
            )

        self.accept()




