import os

from PyQt5.QtGui import QFont, QFontMetrics

dirname = os.path.dirname(__file__)
resourse_directory = os.path.join(dirname, '../resource')


def getResourcePath(resource_name: str) -> str:
    return os.path.join(resourse_directory, resource_name)


def fitTextToWidth(text: str, font: QFont, width: int) -> QFont:
    text_width = QFontMetrics(font).horizontalAdvance(text)
    step = font.pointSize() / 20
    new_font = QFont(font)

    while text_width > width:
        new_font.setPointSizeF(max(0, new_font.pointSize() - step))
        text_width = QFontMetrics(new_font).horizontalAdvance(text)

    return new_font
