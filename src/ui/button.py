from typing import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QPushButton, QSizePolicy, QApplication, QWidget, QVBoxLayout, QSlider


class Button(QPushButton):
    def __init__(self, text: str, slot: Callable) -> None:
        super().__init__(text)
        self.clicked.connect(slot)

        self.setMinimumSize(25, 25)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,
                                       QSizePolicy.Minimum))

        self.setFocusPolicy(Qt.NoFocus)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        size = min(self.width(), self.height())
        font_size = size * 0.33  # 50 / 16 (button size / font size)
        font = self.font()
        font.setPointSize(int(font_size))
        self.setFont(font)
