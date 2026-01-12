# main.py
import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from ui.ui_table import ProformaTableWindow
from ui.ui_main import MainWindow

def main():
    app = QApplication(sys.argv)

    # 🟢 Crear la ventana principal de la tabla
    table_window = ProformaTableWindow()

    # 🟢 Crear el panel superior, pasándole la tabla
    control_panel = MainWindow(table_window)

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
