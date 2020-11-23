from PyQt5.QtCore import Qt, QModelIndex, QPoint
from PyQt5.QtGui import QKeyEvent, QKeySequence
from PyQt5.QtWidgets import QListView, QAbstractItemView, QApplication, QMenu, QAction


class HistoryListView(QListView):
    def __init__(self, parent=None) -> None:
        super(HistoryListView, self).__init__(parent)

        self.setMovement(QListView.Snap)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self._context_menu = None

    def keyPressEvent(self, event: QKeyEvent) -> None:
        index = self.currentIndex()

        if event.matches(QKeySequence.Cut):
            self._cutSelectedEquation(index)

    def _deleteSelectedEquations(self) -> None:
        for index in reversed(sorted(self.selectedIndexes(), key=QModelIndex.row)):
            self.model().removeRow(index.row(), QModelIndex())

    def _clear(self) -> None:
        self.model().clear()

    def _copySelectedEquations(self) -> None:
        text_to_copy = ''
        for index in self.selectedIndexes():
            text_to_copy += f'{self.model().data(index, Qt.DisplayRole)}\n'
        text_to_copy = text_to_copy.replace('√', 'V')

        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)

    def _copySelectedExpressions(self) -> None:
        text_to_copy = ''
        for index in self.selectedIndexes():
            text_to_copy += f'{self.model().data(index, Qt.UserRole)}\n'
        text_to_copy = text_to_copy.replace('√', 'V')

        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)

    def _cutSelectedEquations(self) -> None:
        self._copySelectedEquations()
        self._deleteSelectedEquations()

    def _editSelectedExpression(self) -> None:
        pass

    def _createContextMenu(self) -> None:
        self._context_menu = QMenu()

        self._context_menu.addAction('Copy equations')
        self._context_menu.addAction('Cut equations')
        self._context_menu.addAction('Copy expressions')
        self._context_menu.addAction('Edit expressions')
        self._context_menu.addAction('Delete')

        self._context_menu.addSeparator()

        self._context_menu.addAction('Clear')
        self._context_menu.addAction('Save')

    def _handleContextAction(self, action: QAction) -> None:
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

    def _updateContextMenu(self) -> None:
        if not self._context_menu:
            self._createContextMenu()

        indexes = self.selectedIndexes()
        if not indexes:
            self._context_menu.setDisabled(True)
        elif len(indexes) == 1:
            self._context_menu.setDisabled(False)
            self._context_menu.actions()[3].setDisabled(True)
        else:
            self._context_menu.setDisabled(False)

    def showContextMenu(self, pos: QPoint) -> None:
        if not self._context_menu:
            self._createContextMenu()

        self._updateContextMenu()

        action = self._context_menu.exec_(self.mapToGlobal(pos))
        if action is not None:
            self._handleContextAction(action)
