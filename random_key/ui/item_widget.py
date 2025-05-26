from PySide6.QtWidgets import (
    QSlider,
    QSpinBox,
    QFormLayout,
    QCheckBox,
    QLineEdit,
    QFrame,
)

from PySide6.QtCore import Qt, Signal

from .widgets import SearchableStrictComboBox


class ItemParameterWidget(QFrame):

    default_style = """
        #formFrame {
            border: 2px solid #6894b0;
            border-radius: 8px;
            padding: 1px;
            background-color: #474747;
        }
        """

    values_changed = Signal(object)
    """When any of the widgets values change emits the object and its value"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("formFrame")

        self._is_disabled = False
        self._is_active = True

        item_form_layout = QFormLayout()

        self.selector = SearchableStrictComboBox()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(50)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)

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
        item_form_layout.addRow("", self.checkbox)

        self.setLayout(item_form_layout)
        self.setFrameShape(QFrame.StyledPanel)

        self.setStyleSheet(self.default_style)

        self.checkbox.stateChanged.connect(
            lambda state, s=self.slider: s.setEnabled(state == 2)
        )

        self._setup_signals()

    def add_palette_items(self, palette: dict[str, str]) -> None:

        for display_name, path in palette.items():
            self.selector.add_item(display_name, path)
            # combo->setItemIcon(0, *icon);

    def _setup_signals(self):

        self.min_amount.valueChanged.connect(self.dummy)
        self.max_amount.valueChanged.connect(self.dummy)
        self.slider.valueChanged.connect(self.dummy)
        self.selector.currentTextChanged.connect(self.dummy)
        self.checkbox.clicked.connect(self.dummy)

    def dummy(self, *args):

        self.values_changed.emit(self)

    def display_active(self, value):

        if value:
            self.setStyleSheet(
                """
        #formFrame {
            border: 2px solid #e8e6e6;
            border-radius: 8px;
            padding: 1px;
            background-color: #474747;
        }
        """
            )
        else:
            self.setStyleSheet(
                """
        #formFrame {
            border: 2px solid #6894b0;
            border-radius: 8px;
            padding: 1px;
            background-color: #474747;
        }
        """
            )

    @property
    def is_active(self):
        return True if self.checkbox.isChecked() else False

    def set_disabled(self, value):
        self._is_disabled = value

    def set_active(self, value):

        widgets = [
            self.selector,
            self.slider,
            self.checkbox,
            self.min_amount,
            self.max_amount,
        ]

        for widget in widgets:
            widget.setEnabled(value)
