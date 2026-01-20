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

    def __init__(self, table_window):
        super().__init__()

        self.table_window = table_window
        self.proforma_state = ProformaState()

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
        self.work_combo.addItems(WORK_TYPES)
        layout.addWidget(self.work_combo)

        # ------------------------------
        # Superficie
        # ------------------------------
        layout.addWidget(QLabel("m²:"))
        self.area_spin = QSpinBox()
        self.area_spin.setRange(1, 5000)
        self.area_spin.setValue(10)
        layout.addWidget(self.area_spin)

        # ------------------------------
        # Color
        # ------------------------------
        layout.addWidget(QLabel("Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(COLORS)
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

    # -------------------------------------------------
    # Eventos
    # -------------------------------------------------

    def on_resin_changed(self, _):
        """
        Ajusta el multiplicador por defecto según el sistema de resina.
        El usuario puede modificarlo después manualmente.
        """
        system_key = self.resin_combo.currentData()
        self.multiplier_spin.setValue(
            get_cost_multiplier(system_key)
        )

    # -------------------------------------------------
    # Acciones
    # -------------------------------------------------

    def _collect_form_data(self):
        """Recoge todos los datos del formulario."""
        return dict(
            system_key=self.resin_combo.currentData(),  # 👈 CLAVE INTERNA
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
