import typing

from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt

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
