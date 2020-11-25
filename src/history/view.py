from PyQt5.QtCore import Qt, QModelIndex, QPoint
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QListView, QAbstractItemView, QApplication, QMenu, QToolBar


class HistoryListView(QListView):
    def __init__(self, parent=None) -> None:
        super(HistoryListView, self).__init__(parent)

        self.setMovement(QListView.Snap)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self._context_menu = None

        # Actions
        self._copy_equations_action = None
        self._cut_equations_action = None
        self._copy_expressions_action = None
        self._edit_expression_action = None
        self._delete_action = None
        self._clear_action = None
        self._save_action = None

    def _deleteSelectedEquations(self) -> None:
        for index in reversed(sorted(self.selectedIndexes(), key=QModelIndex.row)):
            self.model().removeRow(index.row(), QModelIndex())

    def _copySelectedEquations(self) -> None:
        equations = []
        for index in self.selectedIndexes():
            equations.append(self.model().data(index, Qt.DisplayRole))
        text_to_copy = '\n'.join(equations)
        text_to_copy = text_to_copy.replace('√', 'V')

        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)

    def _copySelectedExpressions(self) -> None:
        expressions = []
        for index in self.selectedIndexes():
            expressions.append(self.model().data(index, Qt.UserRole))
        text_to_copy = '\n'.join(expressions)
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

        self._copy_equations_action = self._context_menu.addAction('Copy equations')
        self._copy_equations_action.triggered.connect(self._copySelectedEquations)

        self._cut_equations_action = self._context_menu.addAction('Cut equations')
        self._cut_equations_action.triggered.connect(self._cutSelectedEquations)

        self._copy_expressions_action = self._context_menu.addAction('Copy expressions')
        self._copy_expressions_action.triggered.connect(self._copySelectedExpressions)

        self._edit_expression_action = self._context_menu.addAction('Edit expression')
        self._edit_expression_action.triggered.connect(self._editSelectedExpression)

        self._delete_action = self._context_menu.addAction('Delete')
        self._delete_action.setShortcut(QKeySequence.Delete)
        self._delete_action.triggered.connect(self._deleteSelectedEquations)
        self.addAction(self._delete_action)

        self._context_menu.addSeparator()

        self._clear_action = self._context_menu.addAction('Clear')
        self._clear_action.triggered.connect(self.model().clear)

        self._save_action = self._context_menu.addAction('Save')
        self._save_action.triggered.connect(self.model().saveHistory)

    def _setActionsEnabled(self, enable: bool = True) -> None:
        self._copy_equations_action.setEnabled(enable)
        self._cut_equations_action.setEnabled(enable)
        self._copy_expressions_action.setEnabled(enable)
        self._edit_expression_action.setEnabled(enable)
        self._delete_action.setEnabled(enable)
        self._clear_action.setEnabled(enable)
        self._save_action.setEnabled(enable)

    def _updateContextMenu(self) -> None:
        if not self._context_menu:
            self._createContextMenu()

        if self.model().rowCount(QModelIndex()) <= 0:
            self._setActionsEnabled(False)
        else:
            indexes = self.selectedIndexes()
            if not indexes:
                self._setActionsEnabled(False)
            elif len(indexes) == 1:
                self._setActionsEnabled(True)
            else:
                self._setActionsEnabled(True)
                self._edit_expression_action.setDisabled(True)

            self._clear_action.setEnabled(True)
            self._save_action.setEnabled(True)

    def showContextMenu(self, pos: QPoint) -> None:
        if not self._context_menu:
            self._createContextMenu()

        self._updateContextMenu()

        self._context_menu.exec_(self.mapToGlobal(pos))
