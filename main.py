import sys
from PySide6.QtWidgets import QApplication
from ui.ui_table import ProformaTableWindow

app = QApplication(sys.argv)

window = ProformaTableWindow()
window.show()

sys.exit(app.exec())
