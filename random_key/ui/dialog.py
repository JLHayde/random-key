from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QSpinBox,
    QFormLayout,
    QPushButton,
    QFrame,
    QScrollArea,
    QGridLayout,
)

from PySide6.QtCore import Qt, QPoint
from PySide6.QtCore import QSettings

settings = QSettings("MCTools", "RandomKeys")


class AppDialog(QWidget):
    def __init__(self):
        super().__init__()

        self._current_index = 0
        self._max_index = 0

        self.setMouseTracking(True)

        # Main vertical layout
        self.outer_layout = QVBoxLayout()

        # Horizontal layout for sliders and labels
        self.sliders_layout = QGridLayout()

        self.outer_layout.addLayout(self.sliders_layout)

        bottom_frame = QFrame()
        bottom_frame.setFrameShape(QFrame.StyledPanel)
        bottom_frame.setObjectName("bottomformFrame")  # so we can style it

        # Add Max Height spin box (no behavior attached)
        form_layout = QFormLayout()
        self.max_height_spinbox = QSpinBox()
        self.max_height_spinbox.setRange(0, 512)
        self.max_height_spinbox.setValue(32)

        self._drag_active = False
        self._drag_start_pos = QPoint()

        self.current_key = QLabel()
        self.next_key = QLabel()
        self.progress = QSlider(Qt.Horizontal)

        self.buffer_button = QPushButton("Regenerate Buffer")

        form_layout.addRow("Max Height:", self.max_height_spinbox)
        form_layout.addRow("Current Key:", self.current_key)
        form_layout.addRow("Next Key:", self.next_key)
        form_layout.addRow("Progress:", self.progress)
        form_layout.addRow("", self.buffer_button)

        bottom_frame.setLayout(form_layout)
        bottom_frame.setStyleSheet(
            """
        #bottomformFrame {
            border: 2px solid #4A90E2;
            border-radius: 8px;
            padding: 1px;
            background-color: #474747;
        }
        """
        )

        # self.preview_widget = PreviewWidget()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setMinimumHeight(100)

        container = QWidget()
        self.prewiew_layout = QHBoxLayout(container)
        self.prewiew_layout.setSpacing(0)  # No spacing between images
        self.prewiew_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        self.prewiew_layout.setAlignment(Qt.AlignLeft)  # Align to the left

        # Set layout and scroll area
        container.setLayout(self.prewiew_layout)
        scroll_area.setWidget(container)

        self.outer_layout.addWidget(scroll_area)

        self.outer_layout.addWidget(bottom_frame)
