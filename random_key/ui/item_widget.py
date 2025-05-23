import os
import pathlib
import random
import keyboard
from copy import deepcopy, copy
import random
import pprint

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
    QScrollArea,
    QComboBox,
    QCompleter,
)

from PySide6.QtGui import QPixmap, QStandardItemModel, QIcon, QStandardItem
from PySide6.QtCore import Qt, QPoint, QSettings, QSortFilterProxyModel
import sys

from .widgets import SearchableStrictComboBox


class ItemParameterWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("formFrame")

        item_form_layout = QFormLayout()

        self.selector = SearchableStrictComboBox()

        self.slider = QSlider(Qt.Vertical)
        self.slider.setRange(1, 100)
        self.slider.setValue(50)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)

        self.checkbox = QCheckBox()

        self.min_amount = QSpinBox()
        self.min_amount.setValue(1)

        self.max_amount = QSpinBox()
        self.max_amount.setValue(3)
        self.max_amount.setMinimumWidth(70)

        self.no_next = QLineEdit()

        item_form_layout.addRow("item", self.selector)
        item_form_layout.addRow("Prob", self.slider)
        item_form_layout.addRow("Min", self.min_amount)
        item_form_layout.addRow("Max", self.max_amount)
        item_form_layout.addRow("Avoid:", self.no_next)
        item_form_layout.addRow("Enabled:", self.checkbox)

        self.setLayout(item_form_layout)
        self.setFrameShape(QFrame.StyledPanel)

        self.setStyleSheet(
            """
        #formFrame {
            border: 2px solid #4A90E2;
            border-radius: 8px;
            padding: 1px;
            background-color: #474747;
        }
        """
        )
