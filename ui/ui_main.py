from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QComboBox, QDoubleSpinBox, QPushButton, QSpinBox,
    QLineEdit
)
from PySide6.QtCore import Qt

from generator.proforma_generator import generate_proforma
from pricing.multipliers import MULTIPLICADORES

# Tipos de resina
RESIN_TYPES = ["EPOXI", "POLITOP", "IMPRIMACIÓN"]

# Tipos de trabajo / capas
WORK_TYPES = [
    "IMPRIMACIÓN",
    "1 CAPA",
    "2 CAPAS",
    "IMPRIMACIÓN + 1 CAPA",
    "IMPRIMACIÓN + 2 CAPAS"
]

# Opciones de color (ejemplo)
COLOR_OPTIONS = ["VERDE", "GRIS", "BLANCO", "NEGRO"]


class MainWindow(QWidget):
    def __init__(self, table_window):
        super().__init__()
        self.table_window = table_window

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Cliente
        layout.addWidget(QLabel("Nombre:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Teléfono:"))
        self.phone_input = QLineEdit()
        layout.addWidget(self.phone_input)

        # Resina
        layout.addWidget(QLabel("Resina:"))
        self.resin_combo = QComboBox()
        self.resin_combo.addItems(RESIN_TYPES)
        self.resin_combo.currentIndexChanged.connect(self.on_resin_changed)
        layout.addWidget(self.resin_combo)

        # Trabajo / Capas
        layout.addWidget(QLabel("Trabajo:"))
        self.work_combo = QComboBox()
        self.work_combo.addItems(WORK_TYPES)
        layout.addWidget(self.work_combo)

        # m²
        layout.addWidget(QLabel("m²:"))
        self.area_spin = QSpinBox()
        self.area_spin.setRange(1, 1000)
        self.area_spin.setValue(10)
        layout.addWidget(self.area_spin)

        # Multiplicador de precio
        layout.addWidget(QLabel("Multiplicador:"))
        self.multiplier_spin = QDoubleSpinBox()
        self.multiplier_spin.setRange(0.1, 10.0)
        self.multiplier_spin.setSingleStep(0.1)
        self.multiplier_spin.setValue(1.0)
        layout.addWidget(self.multiplier_spin)

        # Color
        layout.addWidget(QLabel("Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(COLOR_OPTIONS)
        layout.addWidget(self.color_combo)

        # Botón Generar Proforma
        self.generate_btn = QPushButton("Generar Proforma")
        self.generate_btn.clicked.connect(self.generate_proforma_rows)
        layout.addWidget(self.generate_btn)

        # Inicializar multiplicador según resina
        self.on_resin_changed(self.resin_combo.currentIndex())

    def on_resin_changed(self, index):
        resin = self.resin_combo.currentText()
        self.multiplier_spin.setValue(MULTIPLICADORES.get(resin, 1.0))

    # ui/ui_main.py (solo fragmentos relevantes con cambios)
    # Al final de generate_proforma_rows:
    def generate_proforma_rows(self):
        resin = self.resin_combo.currentText()
        work_type = self.work_combo.currentText()
        area = self.area_spin.value()
        multiplier = self.multiplier_spin.value()
        color = self.color_combo.currentText()
        customer_name = self.name_input.text()
        customer_phone = self.phone_input.text()

        # Generar filas completas (se limpia todo)
        rows = generate_proforma(
            table_window=self.table_window,
            resin_type=resin,
            work_type=work_type,
            area_m2=area,
            multiplier=multiplier,
            color=color,
            customer_name=customer_name,
            customer_phone=customer_phone
        )


