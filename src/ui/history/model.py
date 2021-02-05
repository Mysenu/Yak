import typing

from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt, QMimeData
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog

from src.expression import calculateExpr, isValidExpression, toEditableExpr, fromEditableExpr
from .utils import saveHistoryToFile, addExpressionToHistoryCache, clearHistoryCache

ExpressionRole = Qt.UserRole
ResultRole = Qt.UserRole + 1


class HistoryListModel(QAbstractListModel):
    def __init__(self, parent=None) -> None:
        super(HistoryListModel, self).__init__(parent)

        self._expressions = []
        self._font = None

        self.need_clear_history = True

    def addExpression(self, expr: str, index: int = 0, save_to_cache: bool = True) -> None:
        if not isValidExpression(expr):
            return

        if self.rowCount(QModelIndex()):
            latest_expr_index = self.index(0, 0)
            latest_expr = self.data(latest_expr_index, ExpressionRole)
            if latest_expr == expr:
                return

        if self.need_clear_history and self._expressions:
            self.need_clear_history = False

        self.beginResetModel()
        self._expressions.insert(index, expr)
        self.endResetModel()

        if save_to_cache:
            if self.need_clear_history:
                clearHistoryCache()
                self.need_clear_history = False

            addExpressionToHistoryCache(expr)

    def addExpressions(self, expressions: list) -> None:
        for expression in expressions:
            self.addExpression(expression, save_to_cache=False)

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self._expressions)

    def data(self, index: QModelIndex, role: int) -> typing.Any:
        if not index.isValid():
            return None

        expression = self._expressions[index.row()]

        if role == Qt.DisplayRole:
            return f'{expression} = {calculateExpr(expression)}'
        elif role == Qt.FontRole:
            return self._font
        elif role == Qt.EditRole:
            return expression
        elif role == ExpressionRole:
            return expression
        elif role == ResultRole:
            return calculateExpr(expression)

    def clear(self) -> None:
        self.beginResetModel()
        self._expressions.clear()
        clearHistoryCache()
        self.endResetModel()

    def saveHistory(self) -> None:
        if self.rowCount(QModelIndex()) == 0:
            return

        file_path, _ = QFileDialog.getSaveFileName(filter='*.txt')

        if not file_path:
            return

        expressions = self.equations()
        saveHistoryToFile(expressions, file_path)

    def equations(self) -> typing.List[str]:
        equations_list = []
        for expression in self._expressions:
            equations_list.append(f'{expression} = {calculateExpr(expression)}')
        return equations_list

    def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        self.beginInsertRows(parent, row, row + count - 1)
        for _ in range(count):
            self._expressions.insert(row, None)
        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        self.beginRemoveRows(parent, row, row + count - 1)
        del self._expressions[row:row + count]
        self.endRemoveRows()
        return True

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if not index.isValid():
            return False

        value = fromEditableExpr(value.lower())

        if not isValidExpression(value):
            return False

        if role == Qt.EditRole:
            self._expressions[index.row()] = value
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index: QModelIndex) -> int:
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled

    def supportedDropActions(self) -> int:
        return Qt.MoveAction

    def canDropMimeData(self, data: QMimeData, action: int, row: int, column: int, parent: QModelIndex) -> bool:
        return action == Qt.MoveAction and data.hasText()

    def mimeData(self, indexes: typing.List[QModelIndex]) -> QMimeData:
        mime_data = QMimeData()
        expressions = []
        for index in indexes:
            if index.isValid():
                text = toEditableExpr(self.data(index, ExpressionRole))
                expressions.append(text)
        mime_data.setText('\n'.join(expressions))
        return mime_data

    def dropMimeData(self, data: QMimeData, action: int, row: int, column: int, parent: QModelIndex) -> bool:
        if not self.canDropMimeData(data, action, row, column, parent):
            return False

        if row < 0:
            row = self.rowCount(QModelIndex())
            self.insertRow(row, QModelIndex())
        else:
            self.insertRow(row, QModelIndex())

        index = self.index(row, 0, QModelIndex())
        text = fromEditableExpr(data.text().lower())
        self.setData(index, text, Qt.EditRole)

        return True
