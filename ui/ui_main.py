# ui/ui_main.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout,
    QComboBox, QDoubleSpinBox, QPushButton,
    QSpinBox, QLineEdit
)
from PySide6.QtCore import Qt

from generator.proforma_generator import generate_proforma
from generator.resin_config import RESIN_SYSTEMS, COLORS, get_cost_multiplier
from state.proforma_state import ProformaState
from db.materials_repository import load_materials
from generator.resin_capabilities import get_valid_work_types
from generator.resin_color_capabilities import get_available_colors
from ui.ui_save_proforma_popup import SaveProformaPopup



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
    """
    Panel superior de la aplicación.
    Controla la generación y acumulación de productos en la proforma.
    """

    def __init__(self, table_window, proforma_state):
        super().__init__()

        self.table_window = table_window
        self.proforma_state = proforma_state
        self.materials = load_materials()
        self.all_work_types = WORK_TYPES.copy()
        self.all_colors = COLORS.copy()
        



        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        layout.setSpacing(12)
        self.setLayout(layout)

        # ------------------------------
        # Cliente
        # ------------------------------
        layout.addWidget(QLabel("Nombre:"))
        self.name_input = QLineEdit()
        self.name_input.setFixedWidth(120)
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Teléfono:"))
        self.phone_input = QLineEdit()
        self.phone_input.setFixedWidth(100)
        layout.addWidget(self.phone_input)

        # ------------------------------
        # Sistema de resina
        # ------------------------------
        layout.addWidget(QLabel("Resina:"))
        self.resin_combo = QComboBox()

        # label visible + system_key interno
        for system_key, data in RESIN_SYSTEMS.items():
            self.resin_combo.addItem(data["label"], system_key)

        self.resin_combo.currentIndexChanged.connect(self.on_resin_changed)
        layout.addWidget(self.resin_combo)

        # ------------------------------
        # Trabajo / capas
        # ------------------------------
        layout.addWidget(QLabel("Trabajo:"))
        self.work_combo = QComboBox()
        self.work_combo.addItems(self.all_work_types)
        layout.addWidget(self.work_combo)

        # ------------------------------
        # Superficie
        # ------------------------------
        layout.addWidget(QLabel("m²:"))
        self.area_spin = QSpinBox()
        self.area_spin.setRange(1, 5000)
        self.area_spin.setValue(10)
        layout.addWidget(self.area_spin)
        self.area_spin.valueChanged.connect(self.on_area_changed)


        # ------------------------------
        # Color
        # ------------------------------
        layout.addWidget(QLabel("Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(self.all_colors)
        layout.addWidget(self.color_combo)

        # ------------------------------
        # Multiplicador
        # ------------------------------
        layout.addWidget(QLabel("Multiplicador:"))
        self.multiplier_spin = QDoubleSpinBox()
        self.multiplier_spin.setRange(0.1, 10.0)
        self.multiplier_spin.setSingleStep(0.1)
        self.multiplier_spin.setValue(1.0)
        self.multiplier_spin.setFixedWidth(70)
        layout.addWidget(self.multiplier_spin)

        # ------------------------------
        # Botones
        # ------------------------------
        self.new_btn = QPushButton("🆕 Nueva proforma")
        self.new_btn.clicked.connect(self.generate_new_proforma)
        layout.addWidget(self.new_btn)

        self.add_btn = QPushButton("➕ Añadir productos")
        self.add_btn.clicked.connect(self.add_products)
        layout.addWidget(self.add_btn)

        # Inicializar multiplicador según resina inicial
        self.on_resin_changed(self.resin_combo.currentIndex())
        # Supongamos que tienes algo como esto en MainWindow
        self.table_window.product_list.itemClicked.connect(self.on_product_selected)

        self.save_btn = QPushButton("💾 Guardar proforma")
        self.save_btn.clicked.connect(self.open_save_proforma_popup)
        layout.addWidget(self.save_btn)



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
        
        popup = SaveProformaPopup(
            parent=self,
            proforma_state=self.proforma_state,
            ui_data=self._collect_form_data()
        )
        popup.exec()

