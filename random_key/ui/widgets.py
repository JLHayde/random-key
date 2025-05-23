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


class SearchableStrictComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)

        self.setMinimumWidth(120)

        # Item model
        self.model_ = QStandardItemModel(self)
        self.setModel(self.model_)

        # Filtering model
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setSourceModel(self.model_)

        # Completer setup
        self.completer = QCompleter(self.proxy_model, self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(self.completer)

        # Link text input to filtering
        self.lineEdit().textEdited.connect(self.proxy_model.setFilterFixedString)

        # Validate text on focus out or enter
        self.lineEdit().editingFinished.connect(self.validate_input)

    def add_item(self, text, icon_path=None):
        item = QStandardItem(text)
        if icon_path:
            item.setIcon(QIcon(icon_path))
        self.model_.appendRow(item)

    def validate_input(self):
        text = self.currentText()
        match_found = False

        for row in range(self.model_.rowCount()):
            if self.model_.item(row).text().lower() == text.lower():
                self.setCurrentIndex(row)
                match_found = True
                break

        if not match_found:
            self.setCurrentIndex(-1)
            self.lineEdit().clear()
