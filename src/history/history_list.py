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


class HistoryListView(QListView):
    def __init__(self, parent=None) -> None:
        super(HistoryListView, self).__init__(parent)

        self.setMovement(QListView.Snap)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self._contextMenu = None

    def keyPressEvent(self, event: QKeyEvent) -> None:
        index = self.currentIndex()

        if event.matches(QKeySequence.Cut):
            self._cutSelectedEquation(index)

    def _deleteSelectedEquations(self) -> None:
        for index in self.selectedIndexes():
            self.model().removeRow(index.row(), QModelIndex())

    def _clear(self) -> None:
        self.model().clear()

    def _copySelectedEquations(self) -> None:
        text_to_copy = ''
        for index in self.selectedIndexes():
            text_to_copy += f'{self.model().data(index, Qt.DisplayRole)}/n'
        text_to_copy = text_to_copy.replace('√', 'V')

        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)

    def _copySelectedExpressions(self) -> None:
        text_to_copy = ''
        for index in self.selectedIndexes():
            text_to_copy += f'{self.model().data(index, Qt.UserRole)}/n'
        text_to_copy = text_to_copy.replace('√', 'V')

        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)

    def _cutSelectedEquations(self) -> None:
        self._copySelectedEquations()
        self._deleteSelectedEquations()

    def _editSelectedExpression(self) -> None:
        pass

    def contextMenu(self, pos: QPoint) -> None:
        if not self._contextMenu:
            self._contextMenu = QMenu()
            self._contextMenu.addAction('Copy equations')
            self._contextMenu.addAction('Cut equations')
            self._contextMenu.addAction('Copy expressions')
            self._contextMenu.addAction('Edit expressions')
            self._contextMenu.addAction('Delete')

            self._contextMenu.addSeparator()
            self._contextMenu.addAction('Clear history')
            self._contextMenu.addAction('Save history')

        indexes = self.selectedIndexes()
        if not indexes:
            self._contextMenu.setDisabled(True)
        elif len(indexes) == 1:
            self._contextMenu.setDisabled(False)
            self._contextMenu.actions()[3].setDisabled(True)
        else:
            self._contextMenu.setDisabled(False)
        action = self._contextMenu.exec_(self.mapToGlobal(pos))
        if action:
            action_text = action.text()
            if action_text == 'Delete':
                self._deleteSelectedEquations()
            elif action_text == 'Copy equations':
                self._copySelectedEquations()
            elif action_text == 'Copy expressions':
                self._copySelectedExpressions()
            elif action_text == 'Cut equations':
                self._cutSelectedEquations()
            elif action_text == 'Edit expressions':
                self._editSelectedExpression()
            elif action_text == 'Save history':
                self.model().saveHustory()
            elif action_text == 'Clear history':
                self._clear()
