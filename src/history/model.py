import typing

from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt, QMimeData, QByteArray
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from src.core.core import saveHistoryToFile
from src.expression.calculate import calculate
from src.expression.check import isValidExpression
from src.expression.prepare import toEditableExpr, fromEditableExpr

ExpressionRole = Qt.UserRole
ResultRole = Qt.UserRole + 1


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

        if role == Qt.DisplayRole:
            return f'{expression} = {calculate(expression)}'
        elif role == Qt.EditRole:
            return expression
        elif role == ExpressionRole:
            return expression
        elif role == ResultRole:
            return calculate(expression)

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

    def supportedDropActions(self) -> typing.Union[int, typing.Iterable[int]]:
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
