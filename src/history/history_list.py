import typing

from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt, QMimeData, QByteArray, QDataStream, QIODevice, QTextStream

from src.expression.expressions import calculate


class HistoryListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(HistoryListModel, self).__init__(parent)

        self._expressions = []

    def addExpression(self, expr: str) -> None:
        self.beginResetModel()
        self._expressions.insert(0, expr)
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

    def clearData(self):
        self.beginResetModel()
        self._expressions.clear()
        self.endResetModel()

    def notEmptyList(self):
        if self._expressions:
            return True
        return False

    def expressionsData(self):
        equation = []
        for expression in self._expressions:
            equation.append(f'{expression} = {calculate(expression)}')

        return equation

    def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        self.beginInsertRows(parent, row, row + count - 1)
        self._expressions.insert(row, self._expressions[row - 1])
        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        self.beginRemoveRows(parent, row, row + count + 1)
        self._expressions.pop(row)
        self.endRemoveRows()
        return True

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if index.isValid() and role == Qt.DisplayRole:
            self._expressions[index.row()] = value
            return True
        return False

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled

    def supportedDropActions(self):
        return Qt.MoveAction

    def canDropMimeData(self, data, action, row, column, parent):
        return action == Qt.MoveAction and data.hasFormat('text/plain')

    def mimeData(self, indexes):
        mime_data = QMimeData()
        for index in indexes:
            if index.isValid():
                mime_data.setText(self.data(index, Qt.UserRole))
        return mime_data

    def dropMimeData(self, data, action, row, column, parent):
        if row < 0:
            return False

        if not self.canDropMimeData(data, action, row, column, parent):
            return False

        if action == Qt.IgnoreAction:
            return True
        elif action != Qt.MoveAction:
            return False

        encoded_data = data.data('text/plain')
        stream = QTextStream(encoded_data, QIODevice.ReadOnly)

        self.insertRow(row, QModelIndex())
        index = self.index(row, 0, QModelIndex())
        self.setData(index, stream.readAll(), Qt.DisplayRole)

        return True
