import os
import pprint

from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSettings, QThread, QObject, Signal, Slot

from pynput import mouse
import keyboard

from .ui.dialog import AppDialog
from .ui.item_widget import ItemParameterWidget
from .sequences import WFC1D
from .constants import APP_NAME, GROUP_NAME, REMAP_ITEMS

settings = QSettings(GROUP_NAME, APP_NAME)


class ItemIconWorker(QObject):
    """
    Generates the palette as a QIcon's Emits signal
    when each icon has be been generated.
    """

    item_ready = Signal(int, QIcon)
    finished = Signal()

    def __init__(self, item_mappings: dict, parent=None):
        super().__init__()

        self.item_mappings = item_mappings

    def run(self):

        for k, v in enumerate(list(self.item_mappings.values())):
            icon = QIcon(v)
            self.item_ready.emit(k, icon)

        self.finished.emit()


class RandomKeyDialog(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Random Block Selector")
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.ui = AppDialog()

        self._item_widgets: list[ItemParameterWidget] = []
        self.active = True
        self.buffer: list[tuple[str, int]] = []
        self.palette = self._build_palette()

        # Mouse Lister
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

        rows, cols = 1, 9
        for index in range(0, rows * cols):
            row = index // cols
            col = index % cols
            self.add_item_widget(row, col)

        # Threads and workers
        self._icon_thread = QThread()
        self._icon_worker = ItemIconWorker(self.palette)

        self._preview_thread = QThread()
        self._preview_worker = ItemIconWorker(self.palette)

        # UI Setup
        self._restore_values()
        self._generate_buffer()
        self.draw_palette_from_buffer()

        # Connections
        self.ui.max_height_spinbox.valueChanged.connect(self._generate_buffer)
        self.ui.buffer_button.clicked.connect(self._generate_buffer)
        for i in self._item_widgets:
            i.values_changed.connect(self.on_values_changed)

        # Setup Icons for item selector in thread
        self._icon_worker.moveToThread(self._icon_thread)
        self._icon_thread.started.connect(self._icon_worker.run)
        self._icon_worker.item_ready.connect(self.on_item_icons_generated)
        self._icon_worker.finished.connect(self._icon_thread.quit)
        self._icon_thread.start()

        self.setLayout(self.ui.outer_layout)
        self.resize(700, 400)

    # Qt Events
    def closeEvent(self, event) -> None:
        """
        Re-implementation of closeEvent to save UI Values.
        :param event:
        :return:
        """
        print("App Closing...")
        self._save_values()
        super().closeEvent(event)

    # Init methods
    @staticmethod
    def _build_palette() -> dict[str, str]:
        """
        Build a mapped palette from display name to texture path.
        :return:
        """

        # Path to palette
        palette_dir = os.path.join(
            os.path.dirname(__file__), os.pardir, "resources", "palette"
        )
        palette = []

        for i in os.listdir(palette_dir):
            f_name = i.split(".")[0]
            f_name = REMAP_ITEMS.get(f_name, f_name)
            f_name = f_name.replace("_", " ").title()

            full_path = os.path.join(palette_dir, i)
            palette.append((f_name, full_path))

        # Sort by the remapped and formatted name
        palette.sort(key=lambda x: x[0])

        palette_dict = {name: path for name, path in palette}
        return palette_dict

    def on_item_icons_generated(self, index: int, icon: QIcon) -> None:
        """
        Callback method for item icons generated in thread. Adds them to
        each item's, Item selector.
        :param index:
        :param icon:
        :return:
        """

        for widget in self._item_widgets:
            widget.selector.set_icon(index, icon)

    def add_item_widget(self, row: int, column: int) -> None:
        """
        Add item_widget.ItemParameterWidget widget to the Items Layout
        :return:
        """
        item_params_widget = ItemParameterWidget()
        item_params_widget.add_palette_items(self.palette)

        self._item_widgets.append(item_params_widget)
        self.ui.sliders_layout.addWidget(item_params_widget, row, column)

    # User Settings
    def _save_values(self) -> None:
        """
        Saves the Sessions UI values.
        :return:
        """

        settings.setValue("sliders", [x.slider.value() for x in self._item_widgets])
        settings.setValue(
            "enabled", [x.checkbox.isChecked() for x in self._item_widgets]
        )
        settings.setValue("mins", [x.min_amount.value() for x in self._item_widgets])
        settings.setValue("max", [x.max_amount.value() for x in self._item_widgets])
        settings.setValue("avoids", [x.no_next.text() for x in self._item_widgets])
        settings.setValue("max_length", self.ui.max_height_spinbox.value())
        settings.setValue(
            "items", [x.selector.currentIndex() for x in self._item_widgets]
        )
        print("Saved Sessions UI values")

    def _restore_values(self) -> None:
        """
        Restore the UI values from previous session.
        :return:
        """
        self.ui.max_height_spinbox.setValue(settings.value("max_length", type=int))
        for x, val in enumerate(settings.value("sliders", type=list)):
            self._item_widgets[x].slider.setValue(int(val))
        for x, val in enumerate(settings.value("enabled", type=list)):
            val = val == "true"
            self._item_widgets[x].checkbox.setChecked(val)
            self._item_widgets[x].slider.setEnabled(val)
        for x, val in enumerate(settings.value("mins", type=list)):
            self._item_widgets[x].min_amount.setValue(int(val))
        for x, val in enumerate(settings.value("max", type=list)):
            self._item_widgets[x].max_amount.setValue(int(val))
        for x, val in enumerate(settings.value("avoids")):
            self._item_widgets[x].no_next.setText(val)
        for x, val in enumerate(settings.value("items", type=list)):
            self._item_widgets[x].selector.setCurrentIndex(int(val))

        print("Restored Settings")

    # Display
    def draw_palette_from_buffer(self, image_size: int = 64):
        """
        Displays the buffer as A block sequence using the palette resources.
        :return:
        """

        # Generate Paths
        images: list[str] = [self.palette.get(block) for block, _ in self.buffer]

        # Clear the layout
        while self.ui.prewiew_layout.count():
            item = self.ui.prewiew_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for path in images:
            if not path:
                continue
            label = QLabel()
            label.setFixedSize(image_size, image_size)
            pixmap = QPixmap(path).scaled(image_size, image_size, Qt.IgnoreAspectRatio)
            label.setPixmap(pixmap)
            self.ui.prewiew_layout.addWidget(label)

    def on_values_changed(self, widget):

        # if widget.is_active:
        self._generate_buffer()

    def _generate_buffer(self, *args) -> None:
        """
        Build the buffer and update the UI with new values.
        :param args:
        :return:
        """

        self._save_values()
        self.buffer = self.build_rule()
        self._current_index = 0
        self.ui.progress.setRange(0, len(self.buffer))

        self.update_displays()
        self.draw_palette_from_buffer()

    def build_rule(self) -> list[int]:
        """
        Using Wave function and Item parameter rules build the item sequence index buffer
        :return:
        """

        rules = {}
        probabilities = {}

        for x, item_widget in enumerate(self._item_widgets):
            if not item_widget.slider.isEnabled():
                continue

            item_name = item_widget.selector.currentText()
            min_count = item_widget.min_amount.value()
            max_count = item_widget.max_amount.value()
            no_next = [
                int(avoid)
                for avoid in item_widget.no_next.text().split(",")
                if avoid.strip().isdigit()
            ]
            rule = {
                "min_repeat": min_count,
                "max_repeat": max_count,
                "no_next": no_next,
            }

            rules[(item_name, x + 1)] = rule
            probabilities[(item_name, x + 1)] = item_widget.slider.value()

        wfc = WFC1D(
            length=self.ui.max_height_spinbox.value(),
            rules=rules,
            probabilities=probabilities,
        )
        if not rules:
            return []
        else:
            result = wfc.run()
            return result

    def update_displays(self) -> None:

        if self._current_index > len(self.buffer) - 1:
            pass
        else:

            item, cur = self.buffer[self._current_index]

            current_text = "Key: %s, Item: %s" % (cur, item)
            self.ui.current_key.setText(current_text)
            self.ui.progress.setValue(self._current_index)

        if self._current_index + 1 > len(self.buffer) - 1:
            self.ui.next_key.setText("")
        else:
            key = str(self.buffer[self._current_index + 1][1])
            self.ui.next_key.setText(key)

        # for x, i in enumerate(self._item_widgets):
        #    if x == self.buffer[self._current_index][0]:
        #        i.display_active(True)
        #
        #    else:
        #        i.display_active(False)
        # self.draw_palette_from_buffer()

    def on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        """
        Event callback from mouse listener
        :param x:
        :param y:
        :param button:
        :param pressed:
        :return:
        """

        if not pressed and button == mouse.Button.right and self.active:
            self.increment_buffer()

    def increment_buffer(self) -> None:
        """
        Triggered when a right click has been registered, Increment the current
        index in the buffer. Update the displays

        :return:
        """

        self._current_index += 1

        if self._current_index > len(self.buffer) - 1:
            pass
        else:
            key = str(self.buffer[self._current_index - 1][1])
            self.simulate_keypress(key)
        self.update_displays()

    @staticmethod
    def simulate_keypress(key: str) -> None:
        """
        Presses a key on the keyboard.
        :param key:
        :return:
        """
        keyboard.press(key)
        keyboard.release(key)
