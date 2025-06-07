import win32gui

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QFont, QColor

from window_location import get_window_rect, find_minecraft_window


class OverlayWindow(QWidget):
    def __init__(self, text, hwnd, padding=(20, 30)):
        super().__init__()
        self.text = text
        self.color = QColor(230, 230, 230)
        self.font = QFont("Arial", 24, QFont.Bold)
        self.hwnd = hwnd
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.padding = padding
        self.update_position()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(80)

    def set_text(self, text):
        self.text = text

    def update_position(self):
        if not win32gui.IsWindow(self.hwnd):
            self.close()
            return
        rect = get_window_rect(self.hwnd)
        x, y, r, b = rect
        self.setGeometry(x, y, r - x, b - y)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(self.color)
        painter.setFont(self.font)
        pad_x, pad_y = self.padding
        text_rect = QRect(pad_x, pad_y, self.width() - pad_x, self.height() - pad_y)
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignTop, self.text)

    @staticmethod
    def find_game_window():

        results = find_minecraft_window()
        if results:
            overlay = OverlayWindow("", results[0][0])
            overlay.show()
            return overlay
        else:
            print("Window not found.")
