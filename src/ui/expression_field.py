from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QKeySequence, QDropEvent, QResizeEvent
from PyQt5.QtWidgets import QLineEdit, QApplication

from src.expression import VALID_CHARS
from src.expression import fromEditableExpr, toEditableExpr


class ExpressionField(QLineEdit):
    def __init__(self):
        super(ExpressionField, self).__init__()

        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.textChanged.connect(self._autoFormat)

    def _autoFormat(self, expr: str):
        self.blockSignals(True)
        expr_length = len(expr)
        right_indent = min(expr_length - len(expr.rstrip()), 1)
        formatted_expr = f"{' '.join(expr.split())}{' ' * right_indent}"
        if expr != formatted_expr:
            position = self.cursorPosition()
            self.setText(formatted_expr)
            self.setCursorPosition(max(position - 1, 0))
        self.blockSignals(False)

    def canBeAdded(self, text: str, expression: str = None, position: int = None) -> bool:
        return not (set(text) - VALID_CHARS)

    def insert(self, text: str) -> None:
        text = fromEditableExpr(text.lower())

        if self.canBeAdded(text):
            super().insert(text)

    def keyPressEvent(self, event: QKeyEvent):
        char = event.text()
        if (char and ord(char) in range(ord(' '), ord('~') + 1) or char.isalpha()) \
                and event.modifiers() in (Qt.NoModifier, Qt.ShiftModifier):
            if not (set(char) - (VALID_CHARS | set('vV'))):
                self.insert(char)
        else:
            if event.matches(QKeySequence.Cancel):
                self.clear()
            elif event.matches(QKeySequence.Copy):
                if not self.text():
                    return

                if self.selectedText():
                    text_to_copy = self.selectedText()
                else:
                    text_to_copy = self.text()

                text_to_copy = toEditableExpr(text_to_copy)

                clipboard = QApplication.clipboard()
                clipboard.setText(text_to_copy)
            elif event.matches(QKeySequence.Paste):
                clipboard = QApplication.clipboard()
                text = clipboard.text()

                if not text:
                    return

                self.insert(text.strip())
            elif event.matches(QKeySequence.Cut):
                if not self.text():
                    return

                if self.selectedText():
                    text_to_copy = self.selectedText()
                    super().keyPressEvent(event)
                else:
                    text_to_copy = self.text()
                    self.clear()
                text_to_copy = toEditableExpr(text_to_copy)

                clipboard = QApplication.clipboard()
                clipboard.setText(text_to_copy)
            else:
                super().keyPressEvent(event)

    def dropEvent(self, data: QDropEvent) -> None:
        self.insert(data.mimeData().text())

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        font_size = self.height() * 0.4
        font = self.font()
        font.setPointSize(int(font_size))
        self.setFont(font)
