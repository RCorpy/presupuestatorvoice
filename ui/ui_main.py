# ui/ui_main.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout,
    QComboBox, QDoubleSpinBox, QPushButton,
    QSpinBox, QLineEdit, QVBoxLayout
)
from PySide6.QtCore import Qt

from generator.proforma_generator import generate_proforma
from generator.resin_config import RESIN_SYSTEMS, COLORS, get_cost_multiplier
from state.proforma_state import ProformaState
from db.materials_repository import load_materials
from db.proformas_repository import load_proforma_rows, init_db
from generator.resin_capabilities import get_valid_work_types
from generator.resin_color_capabilities import get_available_colors
from ui.ui_save_proforma_popup import SaveProformaPopup
from ui.ui_load_proforma_popup import LoadProformaPopup
from models.proforma_model import ProformaModel





# ------------------------------
# Configuración UI
# ------------------------------

WORK_TYPES = [
    "IMPRIMACION",
    "1 CAPA",
    "2 CAPAS",
    "IMPRIMACION + 1 CAPA",
    "IMPRIMACION + 2 CAPAS",
]


class MainWindow(QWidget):
    def __init__(self, table_window, proforma_state):
        super().__init__()

        self.table_window = table_window
        self.proforma_state = proforma_state

        self.materials = load_materials()
        self.all_work_types = WORK_TYPES.copy()
        self.all_colors = COLORS.copy()
        init_db()

        main_layout = QVBoxLayout()  # ⚠ ahora usamos vertical para dos filas
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

        # ------------------------------
        # GRUPO 1 - Configuración
        # ------------------------------
        group1_layout = QHBoxLayout()
        group1_layout.setSpacing(12)

        # Cliente
        group1_layout.addWidget(QLabel("Nombre:"))
        self.name_input = QLineEdit()
        self.name_input.setFixedWidth(120)
        group1_layout.addWidget(self.name_input)

        group1_layout.addWidget(QLabel("Teléfono:"))
        self.phone_input = QLineEdit()
        self.phone_input.setFixedWidth(100)
        group1_layout.addWidget(self.phone_input)

        # Resina
        group1_layout.addWidget(QLabel("Resina:"))
        self.resin_combo = QComboBox()
        for system_key, data in RESIN_SYSTEMS.items():
            self.resin_combo.addItem(data["label"], system_key)
        self.resin_combo.currentIndexChanged.connect(self.on_resin_changed)
        group1_layout.addWidget(self.resin_combo)

        # Trabajo
        group1_layout.addWidget(QLabel("Trabajo:"))
        self.work_combo = QComboBox()
        self.work_combo.addItems(self.all_work_types)
        group1_layout.addWidget(self.work_combo)

        # m²
        group1_layout.addWidget(QLabel("m²:"))
        self.area_spin = QSpinBox()
        self.area_spin.setRange(1, 5000)
        self.area_spin.setValue(10)
        self.area_spin.valueChanged.connect(self.on_area_changed)
        group1_layout.addWidget(self.area_spin)

        # Color
        group1_layout.addWidget(QLabel("Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(self.all_colors)
        group1_layout.addWidget(self.color_combo)

        # Multiplicador
        group1_layout.addWidget(QLabel("Multiplicador:"))
        self.multiplier_spin = QDoubleSpinBox()
        self.multiplier_spin.setRange(0.1, 10.0)
        self.multiplier_spin.setSingleStep(0.1)
        self.multiplier_spin.setValue(1.0)
        self.multiplier_spin.setFixedWidth(100)
        group1_layout.addWidget(self.multiplier_spin)

        main_layout.addLayout(group1_layout)

        # ------------------------------
        # GRUPO 2 - Acciones
        # ------------------------------
        group2_layout = QHBoxLayout()
        group2_layout.setSpacing(12)

        self.new_btn = QPushButton("⚙️ Generar proforma")
        self.new_btn.clicked.connect(self.generate_new_proforma)
        group2_layout.addWidget(self.new_btn)

        self.add_btn = QPushButton("➕ Añadir productos")
        self.add_btn.clicked.connect(self.add_products)
        group2_layout.addWidget(self.add_btn)

        self.load_btn = QPushButton("📂 Proformas")
        self.load_btn.clicked.connect(self.open_load_proforma_popup)
        group2_layout.addWidget(self.load_btn)

        self.save_btn = QPushButton("💾 Guardar proforma")
        self.save_btn.clicked.connect(self.open_save_proforma_popup)
        group2_layout.addWidget(self.save_btn)

        main_layout.addLayout(group2_layout)

        # Inicializar multiplicador según resina inicial
        self.on_resin_changed(self.resin_combo.currentIndex())
        self.table_window.product_list.itemClicked.connect(self.on_product_selected)

    # -------------------------------------------------
    # Nuevo método para abrir modal
    # -------------------------------------------------
    def open_load_proforma_popup(self):
        popup = LoadProformaPopup(
            parent=self,
            proforma_model=self.table_window.model
        )

        if popup.exec():
            self.table_window.reload_from_model()




    # -------------------------------------------------
    # Eventos
    # -------------------------------------------------

    def on_resin_changed(self, _):
        system_key = self.resin_combo.currentData()

        # Multiplicador por defecto
        self.multiplier_spin.setValue(
            get_cost_multiplier(system_key)
        )

        # Trabajo
        self.update_work_types_for_resin()

        # 🎨 Colores
        self.update_colors_for_resin()



    # -------------------------------------------------
    # Acciones
    # -------------------------------------------------

    def _collect_form_data(self):
        self.proforma_state.area_m2 = self.area_spin.value()
        return dict(
            system_key=self.resin_combo.currentData(),
            work_type=self.work_combo.currentText(),
            area_m2=self.area_spin.value(),
            multiplier=self.multiplier_spin.value(),
            color=self.color_combo.currentText(),
            customer_name=self.name_input.text(),
            customer_phone=self.phone_input.text(),
        )


    def generate_new_proforma(self):
        """Crea una proforma desde cero."""
        data = self._collect_form_data()

        # 🔥 Reset REAL del estado acumulado
        self.proforma_state.reset()
        self.proforma_state.area_m2 = data["area_m2"]

        generate_proforma(
            table_window=self.table_window,
            proforma_state=self.proforma_state,
            **data
        )

    def add_products(self):
        """Añade productos a la proforma actual."""
        data = self._collect_form_data()

        generate_proforma(
            table_window=self.table_window,
            proforma_state=self.proforma_state,
            **data
        )

    def on_product_selected(self, item):
        multiplier = self.multiplier_spin.value()
        self.table_window.on_product_clicked(item, multiplier)

    def update_work_types_for_resin(self):
        system_key = self.resin_combo.currentData()

        valid_work_types = get_valid_work_types(
            system_key,
            self.all_work_types
        )

        # Reconstruir combo
        self.work_combo.blockSignals(True)
        self.work_combo.clear()
        self.work_combo.addItems(valid_work_types)
        self.work_combo.setCurrentIndex(0)
        self.work_combo.blockSignals(False)

    def update_colors_for_resin(self):
        system_key = self.resin_combo.currentData()

        available_colors = get_available_colors(
            system_key,
            self.materials
        )

        self.color_combo.blockSignals(True)
        self.color_combo.clear()

        if not available_colors:
            self.color_combo.addItem("SIN COLOR")
            self.color_combo.setEnabled(False)
        else:
            self.color_combo.addItems(available_colors)
            self.color_combo.setEnabled(True)
            self.color_combo.setCurrentIndex(0)

        self.color_combo.blockSignals(False)

    def on_area_changed(self, value):
        self.proforma_state.area_m2 = value
        self.table_window.update_summary_panel()

    def open_save_proforma_popup(self):
        #print("on open", self.table_window.model.rows, self.table_window.model)
        popup = SaveProformaPopup(
            parent=self,
            proforma_model=self.table_window.model,
            ui_data=self._collect_form_data()
        )
        popup.exec()

    def load_proforma_from_db(proforma_id: int, proforma_model: ProformaModel):
        """
        Carga una proforma existente desde la DB y la pone en el modelo.
        """
        rows = load_proforma_rows(proforma_id)
        proforma_model.clear()
        for row in rows:
            proforma_model.add_row(row)