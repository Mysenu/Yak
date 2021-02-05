from PyQt5.QtCore import Qt, QModelIndex, QPoint, QAbstractItemModel
from PyQt5.QtGui import QKeySequence, QPainter, QPaintEvent, QFont, QResizeEvent
from PyQt5.QtWidgets import QListView, QAbstractItemView, QApplication, QMenu, QMessageBox, QAction

from src.core.utils import fitTextToWidth
from src.expression import toEditableExpr
from .model import ResultRole, ExpressionRole


class HistoryListView(QListView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setMovement(QListView.Snap)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setTextElideMode(Qt.ElideNone)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        self.setObjectName('History')

        # Menus
        self._context_menu = None
        self._copy_submenu = None

        # Actions
        self._copy_equations_action: QAction
        self._copy_expressions_action: QAction
        self._copy_results_action: QAction
        self._cut_equations_action: QAction
        self._edit_expression_action: QAction
        self._delete_action: QAction
        self._clear_action: QAction
        self._save_action: QAction

        self._createActions()

    def _createActions(self) -> None:
        self._copy_expressions_action = QAction('Expressions')
        self._copy_expressions_action.triggered.connect(self._copySelectedExpressions)
        self._copy_expressions_action.setShortcut(QKeySequence.Copy)
        self.addAction(self._copy_expressions_action)

        self._copy_equations_action = QAction('Equations')
        self._copy_equations_action.triggered.connect(self._copySelectedEquations)
        self._copy_equations_action.setShortcut(Qt.CTRL + Qt.ALT + Qt.Key_C)
        self.addAction(self._copy_equations_action)

        self._copy_results_action = QAction('Results')
        self._copy_results_action.triggered.connect(self._copySelectedResults)
        self._copy_results_action.setShortcut(Qt.CTRL + Qt.SHIFT + Qt.Key_C)
        self.addAction(self._copy_results_action)

        self._cut_equations_action = QAction('Cut equations')
        self._cut_equations_action.triggered.connect(self._cutSelectedEquations)
        self._cut_equations_action.setShortcut(QKeySequence.Cut)
        self.addAction(self._cut_equations_action)

        self._edit_expression_action = QAction('Edit expression')
        self._edit_expression_action.triggered.connect(self._editSelectedExpression)
        self._edit_expression_action.setShortcut(Qt.CTRL + Qt.Key_E)
        self.addAction(self._edit_expression_action)

        self._delete_action = QAction('Delete')
        self._delete_action.triggered.connect(self._deleteSelectedEquations)
        self._delete_action.setShortcut(QKeySequence.Delete)
        self.addAction(self._delete_action)

        self._clear_action = QAction('Clear')
        self._clear_action.triggered.connect(self.clear)

        self._save_action = QAction('Save...')
        self._save_action.triggered.connect(self._saveHistory)
        self._save_action.setShortcut(QKeySequence.Save)
        self.addAction(self._save_action)

    def _deleteSelectedEquations(self) -> None:
        for index in reversed(sorted(self.selectedIndexes(), key=QModelIndex.row)):
            self.model().removeRow(index.row(), QModelIndex())

    def _copySelectedEquations(self) -> None:
        equations = []
        for index in self.selectedIndexes():
            equations.append(self.model().data(index, Qt.DisplayRole))
        text_to_copy = '\n'.join(equations)
        text_to_copy = toEditableExpr(text_to_copy)

        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)

    def _copySelectedExpressions(self) -> None:
        expressions = []
        for index in self.selectedIndexes():
            expressions.append(self.model().data(index, ExpressionRole))
        text_to_copy = '\n'.join(expressions)
        text_to_copy = toEditableExpr(text_to_copy)

        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)

    def _copySelectedResults(self) -> None:
        results = []
        for index in self.selectedIndexes():
            results.append(str(self.model().data(index, ResultRole)))
        text_to_copy = '\n'.join(results)

        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)

    def _cutSelectedEquations(self) -> None:
        self._copySelectedEquations()
        self._deleteSelectedEquations()

    def _editSelectedExpression(self) -> None:
        indexes = self.selectedIndexes()
        if len(indexes) == 1:
            self.edit(indexes[0])

    def _saveHistory(self) -> None:
        self.model().saveHistory()

    def _askUserToClear(self) -> bool:
        button = QMessageBox.question(self, 'Clear', 'Clear all history?')
        return button == QMessageBox.Yes

    def clear(self) -> None:
        if self._askUserToClear():
            self.model().clear()

    def _createContextMenu(self) -> None:
        self._context_menu = QMenu()

        self._copy_submenu = QMenu('Copy')
        self._context_menu.addMenu(self._copy_submenu)

        self._copy_submenu.addAction(self._copy_equations_action)
        self._copy_submenu.addAction(self._copy_expressions_action)
        self._copy_submenu.addAction(self._copy_results_action)

        self._context_menu.addAction(self._cut_equations_action)
        self._context_menu.addAction(self._delete_action)
        self._context_menu.addSeparator()
        self._context_menu.addAction(self._clear_action)
        self._context_menu.addAction(self._save_action)

    def _setActionsEnabled(self, enable: bool = True) -> None:
        self._copy_submenu.setEnabled(enable)
        self._copy_equations_action.setEnabled(enable)
        self._copy_expressions_action.setEnabled(enable)
        self._copy_results_action.setEnabled(enable)

        self._cut_equations_action.setEnabled(enable)
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

    def showContextMenu(self, local_pos: QPoint) -> None:
        if not self._context_menu:
            self._createContextMenu()

        self._updateContextMenu()

        self._context_menu.exec_(self.mapToGlobal(local_pos))

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        font = self.font()
        font.setPointSize(self.height() * 0.13 * 0.4)
        self.viewport().setFont(font)
        self.setFont(font)

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        placeholder_text = 'No history'

        p = QPainter(self.viewport())
        p.setPen(self.palette().placeholderText().color())
        p.setFont(fitTextToWidth(placeholder_text, self.font(), self.width() - 20))

        if not self.model():
            return

        if self.model().rowCount(QModelIndex()) <= 0:
            p.drawText(self.rect(), Qt.AlignCenter, placeholder_text)
