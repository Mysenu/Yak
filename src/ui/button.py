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
