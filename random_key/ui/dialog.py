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

import pynput.mouse
import pynput
from pynput import mouse

from PySide6.QtCore import QSettings

from .widgets import SearchableStrictComboBox
from .item_widget import ItemParameterWidget

settings = QSettings("MCTools", "RandomKeys")


class WFC1D:
    def __init__(self, length, rules, probabilities):
        self.length = length
        self.rules = rules
        self.probabilities = probabilities
        self.positions = [set(rules.keys()) for _ in range(length)]
        self.collapsed = [None] * length

    def entropy(self, options):
        # Shannon entropy approx based on probabilities
        import math

        total_prob = sum(self.probabilities[o] for o in options)
        if total_prob == 0 or len(options) == 1:
            return 0
        entropy = 0
        for o in options:
            p = self.probabilities[o] / total_prob
            entropy -= p * math.log(p)
        return entropy

    def get_lowest_entropy_pos(self):
        min_entropy = float("inf")
        candidates = []
        for i, opts in enumerate(self.positions):
            if self.collapsed[i] is not None:
                continue
            e = self.entropy(opts)
            if e < min_entropy and len(opts) > 0:
                min_entropy = e
                candidates = [i]
            elif e == min_entropy:
                candidates.append(i)
        if not candidates:
            return None
        return random.choice(candidates)

    def collapse(self, pos):
        opts = list(self.positions[pos])
        weights = [self.probabilities[o] for o in opts]
        chosen = random.choices(opts, weights)[0]
        self.positions[pos] = {chosen}
        self.collapsed[pos] = chosen
        return chosen

    def propagate(self, start_pos):
        # Propagate constraints forward and backward
        stack = [start_pos]
        while stack:
            pos = stack.pop()
            val = next(iter(self.positions[pos]))

            # Propagate forward
            if pos + 1 < self.length and self.collapsed[pos + 1] is None:
                before = set(self.positions[pos + 1])
                allowed = {
                    o for o in before if o not in self.rules[val].get("no_next", [])
                }
                if allowed != before:
                    self.positions[pos + 1] = allowed
                    if len(allowed) == 1:
                        self.collapsed[pos + 1] = next(iter(allowed))
                        stack.append(pos + 1)

            # Propagate backward
            if pos - 1 >= 0 and self.collapsed[pos - 1] is None:
                before = set(self.positions[pos - 1])
                allowed = {
                    o for o in before if val not in self.rules[o].get("no_next", [])
                }
                if allowed != before:
                    self.positions[pos - 1] = allowed
                    if len(allowed) == 1:
                        self.collapsed[pos - 1] = next(iter(allowed))
                        stack.append(pos - 1)

    def enforce_repeat_limits(self):
        # This is a bit more complex because repetition is sequential.
        # You could implement this as a post-processing step or more advanced propagation.
        pass

    def run(self):
        while True:
            pos = self.get_lowest_entropy_pos()
            if pos is None:
                break  # done or no positions left

            chosen = self.collapse(pos)
            self.propagate(pos)

        if None in self.collapsed:
            raise RuntimeError("Failed to fully collapse: no valid solutions")

        return self.collapsed


def generate_random_number(
    target_keys: list[int], weights: list[int], length: int
) -> int:
    return random.choices(target_keys, weights=weights, k=length)


class AppDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Random Block Selector")
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self._current_index = 0
        self._max_index = 0

        self._slider_widgets: list[QSlider] = []
        self._min_counts: list[QSpinBox] = []
        self._max_counts: list[QSpinBox] = []
        self._no_next: list[QLineEdit] = []
        self._checkboxes: list[QCheckBox] = []
        self._labels: list[QLineEdit] = []
        self._items: list[SearchableStrictComboBox] = []

        scale = 0.8
        self.setStyleSheet(
            f"""
            * {{
                font-size: {int(10 * scale)}pt;
            }}
        """
        )

        self.buffer = []

        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.palette_dir = os.path.join(
            pathlib.Path(__file__).parent.parent.parent, "resources", "palette"
        )

        self.palette = {}

        for i in os.listdir(self.palette_dir):

            f_name = i.split(".")[0]

            self.palette[f_name] = os.path.join(self.palette_dir, i)

        # self.setStyleSheet("background-color: rgba(0, 0, 0, 1);")

        # Main vertical layout
        outer_layout = QVBoxLayout()

        # Horizontal layout for sliders and labels
        sliders_layout = QHBoxLayout()

        # Create 9 label-slider pairs
        for i in range(1, 10):
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setObjectName("formFrame")

            selector = SearchableStrictComboBox()
            for k, v in self.palette.items():
                selector.addItem(k, v)

            item_form_layout = QFormLayout()

            slider = QSlider(Qt.Vertical)
            slider.setRange(1, 100)
            slider.setValue(50)
            slider.setTickPosition(QSlider.TicksBelow)
            slider.setTickInterval(10)
            # slider.valueChanged.connect(self._generate_buffer)

            checkbox = QCheckBox()
            # checkbox.setChecked(True)

            checkbox.stateChanged.connect(
                lambda state, s=slider: s.setEnabled(state == 2)
            )

            min_amount = QSpinBox()
            min_amount.setValue(1)
            max_amount = QSpinBox()
            max_amount.setValue(3)
            max_amount.setMinimumWidth(70)
            no_next = QLineEdit()

            item_form_layout.addRow("item", selector)
            item_form_layout.addRow("Prob", slider)
            item_form_layout.addRow("Min", min_amount)
            item_form_layout.addRow("Max", max_amount)
            item_form_layout.addRow("Avoid:", no_next)
            item_form_layout.addRow("Enabled:", checkbox)

            self._slider_widgets.append(slider)
            self._min_counts.append(min_amount)
            self._max_counts.append(max_amount)
            self._no_next.append(no_next)
            self._checkboxes.append(checkbox)
            self._items.append(selector)

            frame.setLayout(item_form_layout)
            frame.setFrameShape(QFrame.StyledPanel)

            frame.setStyleSheet(
                """
            #formFrame {
                border: 2px solid #4A90E2;
                border-radius: 8px;
                padding: 1px;
                background-color: #474747;
            }
            """
            )

            sliders_layout.addWidget(frame)

        outer_layout.addLayout(sliders_layout)

        bottom_frame = QFrame()
        bottom_frame.setFrameShape(QFrame.StyledPanel)
        bottom_frame.setObjectName("bottomformFrame")  # so we can style it

        self._slider_widgets[0].valueChanged.connect(self.current_bias)

        # Add Max Height spin box (no behavior attached)
        form_layout = QFormLayout()
        self.max_height_spinbox = QSpinBox()
        self.max_height_spinbox.setRange(0, 512)
        self.max_height_spinbox.setValue(32)
        form_layout.addRow("Max Height:", self.max_height_spinbox)

        self._drag_active = False
        self._drag_start_pos = QPoint()

        self.current_key = QLabel()
        self.next_key = QLabel()
        self.progress = QSlider(Qt.Horizontal)

        buffer_button = QPushButton("Reset")
        buffer_button.clicked.connect(self._generate_buffer)
        form_layout.addRow("Reset Buffer", buffer_button)

        form_layout.addRow("Current Key:", self.current_key)
        form_layout.addRow("Next Key:", self.next_key)
        form_layout.addRow("Progress:", self.progress)

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

        outer_layout.addWidget(bottom_frame)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        container = QWidget()
        self.prewiew_layout = QHBoxLayout(container)
        self.prewiew_layout.setSpacing(0)  # No spacing between images
        self.prewiew_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        self.prewiew_layout.setAlignment(Qt.AlignLeft)  # Align to the left

        image_paths = []

        print(os.getcwd())

        print(self.palette_dir)
        for x, i in enumerate(os.listdir(self.palette_dir)):
            if x > 10:
                break

            image_paths.append(os.path.join(self.palette_dir, i))

        # Set layout and scroll area
        container.setLayout(self.prewiew_layout)
        scroll_area.setWidget(container)

        outer_layout.addWidget(scroll_area)

        self.setLayout(outer_layout)
        self.resize(700, 400)

        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

        self.active = True

        try:
            self._restore_values()
        except Exception as e:
            pass

        self._generate_buffer()

        self.max_height_spinbox.valueChanged.connect(self._generate_buffer)

        self.draw_palette()

        for min_widget, max_widget, slider, item, checkbox in zip(
            self._min_counts,
            self._max_counts,
            self._slider_widgets,
            self._items,
            self._checkboxes,
        ):
            min_widget.valueChanged.connect(self._generate_buffer)
            max_widget.valueChanged.connect(self._generate_buffer)
            slider.valueChanged.connect(self._generate_buffer)
            item.currentTextChanged.connect(self._generate_buffer)
            checkbox.clicked.connect(self._generate_buffer)

    def draw_palette(self):

        images = []

        for block, key in self.buffer:

            if valid_block := self.palette.get(block):
                images.append(valid_block)

        while self.prewiew_layout.count():
            item = self.prewiew_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        size = 64
        for path in images:
            label = QLabel()
            label.setFixedSize(size, size)
            pixmap = QPixmap(path).scaled(size, size, Qt.IgnoreAspectRatio)
            label.setPixmap(pixmap)
            self.prewiew_layout.addWidget(label)

    def _save_values(self) -> None:

        settings.setValue("sliders", [x.value() for x in self._slider_widgets])
        settings.setValue("enabled", [x.isChecked() for x in self._checkboxes])
        settings.setValue("mins", [x.value() for x in self._min_counts])
        settings.setValue("max", [x.value() for x in self._max_counts])
        settings.setValue("avoids", [x.text() for x in self._no_next])
        settings.setValue("max_length", self.max_height_spinbox.value())
        settings.setValue("items", [x.currentText() for x in self._items])

    def _restore_values(self) -> None:
        """
        Restores
        :return:
        """

        for x, val in enumerate(settings.value("sliders", type=list)):
            print(val)
            self._slider_widgets[x].setValue(int(val))
        print("_" * 10)
        for x, val in enumerate(settings.value("enabled", type=list)):
            val = val == "true"
            self._checkboxes[x].setChecked(val)
            self._slider_widgets[x].setEnabled(val)
        print("_" * 10)
        for x, val in enumerate(settings.value("mins", type=list)):
            print(val)
            self._min_counts[x].setValue(int(val))
        print("_" * 10)
        for x, val in enumerate(settings.value("max", type=list)):
            print(val)
            self._max_counts[x].setValue(int(val))
        print("_" * 10)
        for x, val in enumerate(settings.value("avoids")):
            print("-", val)
            self._no_next[x].setText(val)
        print("_" * 10)
        self.max_height_spinbox.setValue(settings.value("max_length", type=int))

        for x, val in enumerate(settings.value("items")):
            print("-", val)
            self._items[x].setCurrentText(val)

        # for i, slider in enumerate(self._slider_widgets):
        #    val =
        #    slider.setValue(val)

    #
    # settings.setValue("sliders", [x.setValue() for x in self._slider_widgets])
    # settings.setValue("enabled", [x.isChecked() for x in self._checkboxes])
    # settings.setValue("mins", [x.value() for x in self._min_counts])
    # settings.setValue("max", [x.value() for x in self._max_counts])
    # settings.setValue("avoids", [x.text() for x in self._no_next])
    # settings.setValue("max_length", self.max_height_spinbox.value())

    def closeEvent(self, event) -> None:

        self._save_values()

    def mousePressEvent(self, event):
        print(event)
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_start_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_start_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False
        event.accept()

    def _generate_buffer(self, *args) -> None:  #

        self._save_values()

        self.buffer = (
            self.build_rule()
        )  # generate_random_number(targets, weights, self.max_height_spinbox.value())
        self._current_index = 0
        self.progress.setRange(0, len(self.buffer))

        # seq = sanitize_index_list(self.buffer, rules)

        self.update_displays()

    def get_preview_paths(self):

        pass

    def update_displays(self) -> None:

        if self._current_index > len(self.buffer) - 1:
            pass
        else:

            self.current_key.setText(str(self.buffer[self._current_index]))
            self.progress.setValue(self._current_index)

        if self._current_index + 1 > len(self.buffer) - 1:
            self.next_key.setText("")
        else:
            key = str(self.buffer[self._current_index + 1][1])
            self.next_key.setText(key)

        self.draw_palette()

    def on_click(self, x, y, button, pressed) -> None:

        if not pressed and button == mouse.Button.right and self.active:
            self.increment()

    def increment(self):

        self._current_index += 1

        if self._current_index > len(self.buffer) - 1:
            pass
        else:
            key = str(self.buffer[self._current_index - 1][1])
            self.simulate_keypress(key)
        self.update_displays()

    def simulate_keypress(self, key):
        keyboard.press(key)
        keyboard.release(key)

    def current_bias(self, *args) -> list[int]:
        return [i.value() for i in self._slider_widgets if i.isEnabled()]

    def build_rule(self) -> list[int]:

        rules = {}
        probabilities = {}

        for x, slider in enumerate(self._slider_widgets):
            if not slider.isEnabled():
                continue

            item = self._items[x].currentText()

            min_count = self._min_counts[x].value()
            max_count = self._max_counts[x].value()
            no_next = [
                int(avoid)
                for avoid in self._no_next[x].text().split(",")
                if avoid.strip().isdigit()
            ]
            rule = {
                "min_repeat": min_count,
                "max_repeat": max_count,
                "no_next": no_next,
            }

            rules[(item, x + 1)] = rule

            probabilities[(item, x + 1)] = slider.value()

        wfc = WFC1D(
            length=self.max_height_spinbox.value(),
            rules=rules,
            probabilities=probabilities,
        )
        if not rules:
            return []
        else:
            pprint.pprint(rules)
            result = wfc.run()
            print(result)
            return result


def sanitize_index_list(index_list, rules):
    from copy import deepcopy
    import random

    modified = deepcopy(index_list)
    repeat_count = 1

    for i in range(1, len(modified)):
        curr = modified[i]
        prev = modified[i - 1]
        prev_rule = rules.get(prev, {})
        curr_rule = rules.get(curr, {})

        # Check for max_repeat violation
        if curr == prev:
            repeat_count += 1
        else:
            repeat_count = 1

        if repeat_count > curr_rule.get("max_repeat", float("inf")):
            # Replace with valid option
            options = [
                n
                for n in range(1, 10)
                if n != curr and n != prev and n not in prev_rule.get("no_next", [])
            ]
            if options:
                modified[i] = random.choice(options)
                repeat_count = 1

        # Check for forbidden adjacency
        if curr in prev_rule.get("no_next", []):
            options = [
                n
                for n in range(1, 10)
                if n != curr and n not in prev_rule.get("no_next", [])
            ]
            if options:
                modified[i] = random.choice(options)
                repeat_count = 1 if modified[i] != prev else repeat_count + 1

    return modified


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    window = AlwaysOnTopWindow()
    window.show()
    sys.exit(app.exec())
