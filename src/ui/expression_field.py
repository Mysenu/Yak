from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QKeySequence
from PyQt5.QtWidgets import QLineEdit, QApplication

from src.expression.check import VALID_CHARS
from src.expression.prepare import fromEditableExpr, toEditableExpr


class ExpressionField(QLineEdit):
    valid_keys = {Qt.Key_Backspace, Qt.Key_Enter, Qt.Key_Return, Qt.Key_C, Qt.Key_V, Qt.Key_X,
                  Qt.Key_Right, Qt.Key_Left, Qt.Key_Delete, Qt.Key_Home, Qt.Key_End}

    def __init__(self):
        super(ExpressionField, self).__init__()

        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font = self.font()
        font.setFamily('Segoe UI')
        font.setPointSize(14)
        self.setFont(font)
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
        text = event.text()
        if not (set(text) - (VALID_CHARS | set('vV'))) and event.modifiers() in (Qt.NoModifier, Qt.ShiftModifier):
            self.insert(text)
        elif event.key() in self.valid_keys:
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
                if event.key() in (Qt.Key_C, Qt.Key_V, Qt.Key_X):
                    return

                super().keyPressEvent(event)

    def dropEvent(self, data: QtGui.QDropEvent) -> None:
        self.insert(data.mimeData().text())
