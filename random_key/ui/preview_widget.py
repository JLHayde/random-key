from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QScrollArea,
)
from PySide6.QtCore import Qt


class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.container = QWidget(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)

        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)  # No spacing between images
        self.layout.setContentsMargins(0, 0, 0, 0)  # No margins
        self.layout.setAlignment(Qt.AlignLeft)  # Align to the left

        # Set layout and scroll area
        self.container.setLayout(self.layout)
        self.scroll_area.setWidget(self.container)

    def add_widget(self, widget):
        self.layout.addWidget(widget)
