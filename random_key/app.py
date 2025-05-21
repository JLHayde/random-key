import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QSpinBox,
    QFormLayout,
    QCheckBox,
    QPushButton,
    QLineEdit,
    QFrame,
)
from PySide6.QtCore import Qt, QPoint

from random_key.ui import dialog


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    window = dialog.AppDialog()
    window.show()
    sys.exit(app.exec())
