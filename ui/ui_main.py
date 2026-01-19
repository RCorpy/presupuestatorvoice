# ui/ui_main.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout,
    QComboBox, QDoubleSpinBox, QPushButton,
    QSpinBox, QLineEdit
)
from PySide6.QtCore import Qt

from generator.proforma_generator import generate_proforma
from pricing.multipliers import MULTIPLICADORES
from state.proforma_state import ProformaState


# ------------------------------
# Configuración UI
# ------------------------------

RESIN_TYPES = ["EPOXI", "POLITOP", "IMPRIMACIÓN"]

WORK_TYPES = [
    "IMPRIMACIÓN",
    "1 CAPA",
    "2 CAPAS",
    "IMPRIMACIÓN + 1 CAPA",
    "IMPRIMACIÓN + 2 CAPAS",
]

COLOR_OPTIONS = ["VERDE", "GRIS", "BLANCO", "NEGRO"]


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
        # Resina
        # ------------------------------
        layout.addWidget(QLabel("Resina:"))
        self.resin_combo = QComboBox()
        self.resin_combo.addItems(RESIN_TYPES)
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
        self.color_combo.addItems(COLOR_OPTIONS)
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

        # Inicializar multiplicador
        self.on_resin_changed(self.resin_combo.currentIndex())

    # -------------------------------------------------
    # Eventos
    # -------------------------------------------------

    def on_resin_changed(self, _):
        resin = self.resin_combo.currentText()
        self.multiplier_spin.setValue(MULTIPLICADORES.get(resin, 1.0))

    # -------------------------------------------------
    # Acciones
    # -------------------------------------------------

    def _collect_form_data(self):
        """Recoge todos los datos del formulario."""
        return dict(
            resin_type=self.resin_combo.currentText(),
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

        # 🔥 RESET REAL DEL ESTADO
        self.proforma_state.reset()

        generate_proforma(
            table_window=self.table_window,
            proforma_state=self.proforma_state,
            **data
        )


    def add_products(self):
        data = self._collect_form_data()

        generate_proforma(
            table_window=self.table_window,
            proforma_state=self.proforma_state,
            **data
        )


