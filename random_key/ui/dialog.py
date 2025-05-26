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

        # Main vertical layout
        self.outer_layout = QVBoxLayout()

        # Horizontal layout for sliders and labels
        self.sliders_layout = QGridLayout()

        self.outer_layout.addLayout(self.sliders_layout)

        self.bottom_frame = QFrame()
        self.bottom_frame.setFrameShape(QFrame.StyledPanel)
        self.bottom_frame.setObjectName("bottomformFrame")  # so we can style it

        # Add Max Height spin box (no behavior attached)
        self.form_layout = QFormLayout()
        self.max_height_spinbox = QSpinBox()
        self.max_height_spinbox.setRange(0, 512)
        self.max_height_spinbox.setValue(32)

        self._drag_active = False
        self._drag_start_pos = QPoint()

        self.current_key = QLabel()
        self.next_key = QLabel()
        self.progress = QSlider(Qt.Horizontal)

        self.buffer_button = QPushButton("Regenerate Buffer")
        self.stop_start_button = QPushButton("Start")
        self.stop_start_button.setCheckable(True)

        self.form_layout.addRow("Max Height:", self.max_height_spinbox)
        self.form_layout.addRow("Current Key:", self.current_key)
        self.form_layout.addRow("Next Key:", self.next_key)
        self.form_layout.addRow("Progress:", self.progress)
        self.form_layout.addRow("", self.buffer_button)
        self.form_layout.addRow("", self.stop_start_button)

        self.bottom_frame.setLayout(self.form_layout)
        self.bottom_frame.setStyleSheet(
            """
        #bottomformFrame {
            border: 2px solid #6894b0;
            border-radius: 8px;
            padding: 1px;
            background-color: #474747;
        }
        """
        )

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setMinimumHeight(100)

        self.scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: 2px solid #6894b0;
                border-radius: 8px;
                padding: 1px;
                background-color: #474747;
            }
        """
        )

        container = QWidget()
        container.setStyleSheet(
            """
            {
                border: 2px solid #6894b0;
                border-radius: 8px;
                padding: 1px;
                background-color: #474747;
            }
        """
        )
        self.preview_layout = QHBoxLayout(container)
        self.preview_layout.setSpacing(0)  # No spacing between images
        self.preview_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        self.preview_layout.setAlignment(Qt.AlignLeft)  # Align to the left

        # Set layout and scroll area

        self.scroll_area.setWidget(container)

        self.outer_layout.addWidget(self.scroll_area)
        self.outer_layout.addWidget(self.bottom_frame)

        self.setLayout(self.outer_layout)
