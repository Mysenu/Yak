import typing

from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt, QMimeData, QPoint
from PyQt5.QtGui import QKeyEvent, QKeySequence
from PyQt5.QtWidgets import QApplication, QListView, QMenu, QFileDialog, QAbstractItemView

from src.core.core import saveHistoryToFile
from src.expression.expressions import calculate
from src.expression.is_valid_expression import isValidExpression


class HistoryListModel(QAbstractListModel):
    def __init__(self, parent=None) -> None:
        super(HistoryListModel, self).__init__(parent)

        self._expressions = []

    def addExpression(self, expr: str, index: int = 0) -> None:
        self.beginResetModel()
        self._expressions.insert(index, expr)
        self.endResetModel()

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self._expressions)

    def data(self, index: QModelIndex, role: int) -> typing.Any:
        if not index.isValid():
            return None

        expression = self._expressions[index.row()]
        equation = f'{expression} = {calculate(expression)}'

        if role == Qt.DisplayRole:
            return equation

        if role == Qt.UserRole:
            return expression

    def clear(self) -> None:
        self.beginResetModel()
        self._expressions.clear()
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
            equations_list.append(f'{expression} = {calculate(expression)}')
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

        if role != Qt.DisplayRole:
            return False

        self._expressions[index.row()] = value
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index: QModelIndex) -> int:
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled

    def supportedDropActions(self) -> typing.Union[int, typing.Iterable[int]]:
        return Qt.MoveAction

    def canDropMimeData(self, data: QMimeData, action: int, row: int, column: int, parent: QModelIndex) -> bool:
        return action == Qt.MoveAction and data.hasText()

    def mimeData(self, indexes: typing.List[QModelIndex]) -> QMimeData:
        mime_data = QMimeData()
        for index in indexes:
            if index.isValid():
                text = self.data(index, Qt.UserRole).replace('√', 'V')
                mime_data.setText(text)
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
        text = data.text().replace('V', '√')
        self.setData(index, text, Qt.DisplayRole)

        return True
