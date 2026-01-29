# main.py
import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from state.proforma_state import ProformaState
from ui.ui_table import ProformaTableWindow
from ui.ui_main import MainWindow
from PySide6.QtGui import QFont


def main():
    base_font = QFont()
    base_font.setPointSize(10)
    
    app = QApplication(sys.argv)
    app.setFont(base_font)
    proforma_state = ProformaState()

    # 🟢 Crear la ventana principal de la tabla
    table_window = ProformaTableWindow(proforma_state)

    # 🟢 Crear el panel superior, pasándole la tabla
    control_panel = MainWindow(table_window, proforma_state)

    # 🟢 Layout principal: vertical, panel arriba, tabla debajo
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.addWidget(control_panel)
    layout.addWidget(table_window)
    container.setLayout(layout)
    container.resize(1700, 650)
    container.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
