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

        self.copy_equations = None
        self.cut_equations = None
        self.copy_expressions = None
        self.edit_expressions = None
        self.delete = None
        self.clear = None
        self.save = None

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

        self.copy_equations = self._context_menu.addAction('Copy equations')
        self.cut_equations = self._context_menu.addAction('Cut equations')
        self.copy_expressions = self._context_menu.addAction('Copy expressions')
        self.edit_expressions = self._context_menu.addAction('Edit expressions')
        self.delete = self._context_menu.addAction('Delete')

        self._context_menu.addSeparator()

        self.clear = self._context_menu.addAction('Clear')
        self.save = self._context_menu.addAction('Save')

        self.copy_equations.triggered.connect(self._copySelectedEquations)
        self.cut_equations.triggered.connect(self._cutSelectedEquations)
        self.copy_expressions.triggered.connect(self._copySelectedExpressions)
        self.edit_expressions.triggered.connect(self._editSelectedExpression)
        self.delete.triggered.connect(self._deleteSelectedEquations)
        self.save.triggered.connect(self.model().saveHistory)
        self.clear.triggered.connect(self._clear)

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

        self._context_menu.exec_(self.mapToGlobal(pos))
