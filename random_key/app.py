import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from random_key.dialog import RandomKeyDialog


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    window = RandomKeyDialog()
    window.show()
    sys.exit(app.exec())
