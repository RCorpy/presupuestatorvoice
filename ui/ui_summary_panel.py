from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

class SummaryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(10)

        # ---- Título ----
        title = QLabel("📊 RESUMEN")
        title.setAlignment(Qt.AlignCenter)
        #title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        layout.addWidget(self._separator())

        # ---- Precio total ----
        self.total_price_label = QLabel("💰 Precio total:\n0 €")
        #self.total_price_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.total_price_label)

        # ---- Precio / m2 ----
        self.price_m2_label = QLabel("📐 Precio / m²:\n0 €/m²")
        #self.price_m2_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.price_m2_label)

        layout.addWidget(self._separator())

        # ---- Consumo ----
        self.consumption_title = QLabel("🧪 CONSUMO")
        #self.consumption_title.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.consumption_title)

        self.gm2_primer_label = QLabel("Imprimación: 0 g/m²")
        self.gm2_layers_label = QLabel("Capas: 0 g/m²")
        self.gm2_total_label = QLabel("Total: 0 g/m²")

        layout.addWidget(self.gm2_primer_label)
        layout.addWidget(self.gm2_layers_label)
        layout.addWidget(self.gm2_total_label)

        layout.addWidget(self._separator())

        # ---- Área ----
        self.area_label = QLabel("Área: 0 m²")
        layout.addWidget(self.area_label)

        layout.addStretch()

    def _separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def update_summary(self, model, area_m2: float):
        total_price = model.get_total_price()
        primer_g_m2, coats_g_m2 = model.get_g_m2_by_phase(area_m2)
        total_g_m2 = primer_g_m2 + coats_g_m2

        # Mantener emojis y texto original
        self.total_price_label.setText(f"💰 Precio total:\n{total_price:.2f} €")

        if area_m2 > 0:
            self.price_m2_label.setText(f"📐 Precio / m²:\n{total_price / area_m2:.2f} €/m²")
            self.gm2_primer_label.setText(f"Imprimación: {primer_g_m2:.0f} g/m²")
            self.gm2_layers_label.setText(f"Capas: {coats_g_m2:.0f} g/m²")
            self.gm2_total_label.setText(f"Total: {total_g_m2:.0f} g/m²")
            self.area_label.setText(f"Área: {area_m2} m²")
        else:
            self.price_m2_label.setText("📐 Precio / m²:\n—")
            self.gm2_primer_label.setText("Imprimación: —")
            self.gm2_layers_label.setText("Capas: —")
            self.gm2_total_label.setText("Total: —")
            self.area_label.setText("Área: 0 m²")

