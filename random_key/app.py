import sys

from PySide6.QtWidgets import QApplication

from random_key.dialog import RandomKeyDialog

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RandomKeyDialog()
    window.show()
    sys.exit(app.exec())
