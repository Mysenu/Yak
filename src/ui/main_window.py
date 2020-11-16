from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListView, qApp, QSizePolicy, \
    QFileDialog, QGridLayout, QApplication, QMenu
from PyQt5.uic.properties import QtCore

from src.core.core import saveHistoryToFile
from src.expression.expressions import calculate
from src.expression.is_valid_expression import isValidExpression, VALID_CHARS
from src.history.history_list import HistoryListModel


class ExpressionField(QLineEdit):
    _valid_keys = {Qt.Key_Backspace, Qt.Key_Enter, Qt.Key_Return, Qt.Key_C, Qt.Key_V, Qt.Key_X,
                   Qt.Key_Right, Qt.Key_Left, Qt.Key_Delete, Qt.Key_Home, Qt.Key_End}

    def __init__(self):
        super(ExpressionField, self).__init__()

        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font = self.font()
        font.setFamily('Segoe UI')
        font.setPointSize(14)
        self.setFont(font)
        self.textChanged.connect(self._autoFormat)

    def _autoFormat(self, expr: str):
        self.blockSignals(True)
        expr_length = len(expr)
        right_indent = min(expr_length - len(expr.rstrip()), 1)
        formatted_expr = f"{' '.join(expr.split())}{' ' * right_indent}"
        if expr != formatted_expr:
            position = self.cursorPosition()
            self.setText(formatted_expr)
            self.setCursorPosition(max(position - 1, 0))
        self.blockSignals(False)

    def canBeAdded(self, text: str, expression: str = None, position: int = None) -> bool:
        return not (set(text) - VALID_CHARS)

    def insert(self, text: str) -> None:
        text = text.lower().replace('v', '√')

        if self.canBeAdded(text):
            super().insert(text)

    def keyPressEvent(self, event: QKeyEvent):
        text = event.text()
        if not (set(text) - (VALID_CHARS | set('vV'))) and event.modifiers() in (Qt.NoModifier, Qt.ShiftModifier):
            self.insert(text)
        elif event.key() in self._valid_keys:
            if event.matches(QKeySequence.Cancel):
                self.clear()
            elif event.matches(QKeySequence.Copy):
                if not self.text():
                    return

                if self.selectedText():
                    text_to_copy = self.selectedText()
                else:
                    text_to_copy = self.text()

                text_to_copy = text_to_copy.replace('√', 'v')

                clipboard = QApplication.clipboard()
                clipboard.setText(text_to_copy)
            elif event.matches(QKeySequence.Paste):
                clipboard = QApplication.clipboard()
                text = clipboard.text()

                if not text:
                    return

                self.insert(text.strip())
            elif event.matches(QKeySequence.Cut):
                if not self.text():
                    return

                if self.selectedText():
                    text_to_copy = self.selectedText()
                else:
                    text_to_copy = self.text()

                self.clear()
                text_to_copy = text_to_copy.replace('√', 'v')

                clipboard = QApplication.clipboard()
                clipboard.setText(text_to_copy)
            else:
                if event.key() in (Qt.Key_C, Qt.Key_V, Qt.Key_X):
                    return

                super().keyPressEvent(event)

    def dropEvent(self, data: QtGui.QDropEvent) -> None:
        self.insert(data.mimeData().text())

    @property
    def valid_keys(self):
        return self._valid_keys


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setWindowTitle('Calculator')
        self.resize(600, 400)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Калькулятор
        calc_layout = QVBoxLayout(self)
        calc_layout.setContentsMargins(4, 4, 4, 4)
        calc_layout.setSpacing(4)
        main_layout.addLayout(calc_layout)

        # Поле ввода
        self.entry_field = ExpressionField()
        self.entry_field.setFixedHeight(40)
        self.entry_field.returnPressed.connect(self._onEvalButtonClick)
        calc_layout.addWidget(self.entry_field)

        # Кнопки калькулятора
        action_layout = QGridLayout()
        calc_layout.addLayout(action_layout)

        self.clean_entry_button = QPushButton('CE')
        self.clean_entry_button.clicked.connect(self.entry_field.clear)
        self.clean_entry_button.setMinimumSize(25, 25)
        self.clean_entry_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        action_layout.addWidget(self.clean_entry_button, 0, 0)

        self.backspace_button = QPushButton('<-')
        action_layout.addWidget(self.backspace_button, 0, 1)
        self.backspace_button.clicked.connect(self.entry_field.backspace)
        self.backspace_button.setMinimumSize(25, 25)
        self.backspace_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.degree_button = QPushButton('^')
        action_layout.addWidget(self.degree_button, 0, 2)
        self.degree_button.clicked.connect(self._onButtonClick)
        self.degree_button.setMinimumSize(25, 25)
        self.degree_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.root_button = QPushButton('√')
        action_layout.addWidget(self.root_button, 0, 3)
        self.root_button.clicked.connect(self._onButtonClick)
        self.root_button.setMinimumSize(25, 25)
        self.root_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        # Вторая строка

        self.bracket1_button = QPushButton('(')
        action_layout.addWidget(self.bracket1_button, 1, 0)
        self.bracket1_button.clicked.connect(self._onButtonClick)
        self.bracket1_button.setMinimumSize(25, 25)
        self.bracket1_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.bracket2_button = QPushButton(')')
        action_layout.addWidget(self.bracket2_button, 1, 1)
        self.bracket2_button.clicked.connect(self._onButtonClick)
        self.bracket2_button.setMinimumSize(25, 25)
        self.bracket2_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.percent_button = QPushButton('%')
        action_layout.addWidget(self.percent_button, 1, 2)
        self.percent_button.clicked.connect(self._onButtonClick)
        self.percent_button.setMinimumSize(25, 25)
        self.percent_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.division_button = QPushButton('/')
        action_layout.addWidget(self.division_button, 1, 3)
        self.division_button.clicked.connect(self._onButtonClick)
        self.division_button.setMinimumSize(25, 25)
        self.division_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        # Третья строка

        self.seven_button = QPushButton('7')
        action_layout.addWidget(self.seven_button, 2, 0)
        self.seven_button.clicked.connect(self._onButtonClick)
        self.seven_button.setMinimumSize(25, 25)
        self.seven_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.eight_button = QPushButton('8')
        action_layout.addWidget(self.eight_button, 2, 1)
        self.eight_button.clicked.connect(self._onButtonClick)
        self.eight_button.setMinimumSize(25, 25)
        self.eight_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.nine_button = QPushButton('9')
        action_layout.addWidget(self.nine_button, 2, 2)
        self.nine_button.clicked.connect(self._onButtonClick)
        self.nine_button.setMinimumSize(25, 25)
        self.nine_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.multiplication_button = QPushButton('*')
        action_layout.addWidget(self.multiplication_button, 2, 3)
        self.multiplication_button.clicked.connect(self._onButtonClick)
        self.multiplication_button.setMinimumSize(25, 25)
        self.multiplication_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        # Четвертая строка

        self.four_button = QPushButton('4')
        action_layout.addWidget(self.four_button, 3, 0)
        self.four_button.clicked.connect(self._onButtonClick)
        self.four_button.setMinimumSize(25, 25)
        self.four_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.five_button = QPushButton('5')
        action_layout.addWidget(self.five_button, 3, 1)
        self.five_button.clicked.connect(self._onButtonClick)
        self.five_button.setMinimumSize(25, 25)
        self.five_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.six_button = QPushButton('6')
        action_layout.addWidget(self.six_button, 3, 2)
        self.six_button.clicked.connect(self._onButtonClick)
        self.six_button.setMinimumSize(25, 25)
        self.six_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.minus_button = QPushButton('-')
        action_layout.addWidget(self.minus_button, 3, 3)
        self.minus_button.clicked.connect(self._onButtonClick)
        self.minus_button.setMinimumSize(25, 25)
        self.minus_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        # Пятая строка

        self.one_button = QPushButton('1')
        action_layout.addWidget(self.one_button, 4, 0)
        self.one_button.clicked.connect(self._onButtonClick)
        self.one_button.setMinimumSize(25, 25)
        self.one_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.two_button = QPushButton('2')
        action_layout.addWidget(self.two_button, 4, 1)
        self.two_button.clicked.connect(self._onButtonClick)
        self.two_button.setMinimumSize(25, 25)
        self.two_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.three_button = QPushButton('3')
        action_layout.addWidget(self.three_button, 4, 2)
        self.three_button.clicked.connect(self._onButtonClick)
        self.three_button.setMinimumSize(25, 25)
        self.three_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.plus_button = QPushButton('+')
        action_layout.addWidget(self.plus_button, 4, 3)
        self.plus_button.clicked.connect(self._onButtonClick)
        self.plus_button.setMinimumSize(25, 25)
        self.plus_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        # Шестая строка

        self.zero_button = QPushButton('0')
        action_layout.addWidget(self.zero_button, 5, 0, 1, 2)
        self.zero_button.clicked.connect(self._onButtonClick)
        self.zero_button.setMinimumSize(25, 25)
        self.zero_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.point_button = QPushButton('.')
        action_layout.addWidget(self.point_button, 5, 2)
        self.point_button.clicked.connect(self._onButtonClick)
        self.point_button.setMinimumSize(25, 25)
        self.point_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.result_button = QPushButton('=')
        action_layout.addWidget(self.result_button, 5, 3)
        self.result_button.setMinimumSize(25, 25)
        self.result_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.result_button.clicked.connect(self._onEvalButtonClick)

        # История
        history_layout = QVBoxLayout(self)
        history_layout.setContentsMargins(4, 4, 4, 4)
        history_layout.setSpacing(4)
        main_layout.addLayout(history_layout)

        self.history_list_model = HistoryListModel()
        self.history_list_view = QListView()
        self.history_list_view.setModel(self.history_list_model)
        self.history_list_view.setMovement(QListView.Snap)
        history_layout.addWidget(self.history_list_view)
        self.history_list_view.doubleClicked.connect(self._setExpressionFromHistory)
        self.history_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list_view.customContextMenuRequested.connect(self.contextMenu)

        history_buttons_layout = QHBoxLayout()
        history_buttons_layout.setContentsMargins(0, 0, 0, 0)
        history_buttons_layout.setSpacing(4)
        history_layout.addLayout(history_buttons_layout)

        self.clear_history_button = QPushButton('Clear')
        history_buttons_layout.addWidget(self.clear_history_button)
        self.clear_history_button.setMinimumSize(30, 25)
        self.clear_history_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.clear_history_button.clicked.connect(self._clearHistoryButton)

        self.save_history_button = QPushButton('Save')
        history_buttons_layout.addWidget(self.save_history_button)
        self.save_history_button.setMinimumSize(30, 25)
        self.save_history_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.save_history_button.clicked.connect(self._saveHistoryButton)

        self.show()

    def _saveHistoryButton(self) -> None:
        if self.history_list_model.rowCount(QModelIndex()) == 0:
            return

        file_path, _ = QFileDialog.getSaveFileName(self, filter='*.txt')

        if not file_path:
            return

        expressions = self.history_list_model.equations()
        saveHistoryToFile(expressions, file_path)

    def _clearHistoryButton(self) -> None:
        self.history_list_model.clearData()

    def _deleteSelectedEquation(self, index: QModelIndex) -> None:
        self.history_list_model.removeRow(index.row(), QModelIndex())

    def _copySelectedEquation(self, index: QModelIndex) -> None:
        self.history_list_model.copySelectedEquation(index)

    def _copySelectedExpression(self, index: QModelIndex) -> None:
        self.history_list_model.copySelectedExpression(index)

    def _cutSelectedEquation(self, index: QModelIndex) -> None:
        self.history_list_model.cutSelectedEquation(index)

    def _editSelectedExpression(self, index: QModelIndex) -> None:
        self.history_list_model.editSelectedExpression(index)

    def _onButtonClick(self) -> None:
        char_to_add = qApp.sender().text()
        self.entry_field.insert(char_to_add)

    def _calculateCurrentExpression(self) -> None:
        result = calculate(self.entry_field.text())
        if result is not None:
            self.entry_field.setText(str(result))

    def _addExpressionToHistory(self) -> None:
        expr = self.entry_field.text()

        if not isValidExpression(expr):
            return

        history_length = self.history_list_model.rowCount(QModelIndex())
        if history_length:
            latest_expr_index = self.history_list_model.index(0, 0)
            latest_expr = self.history_list_model.data(latest_expr_index, Qt.UserRole)
            if latest_expr == expr:
                return

        self.history_list_model.addExpression(expr)

    def _onEvalButtonClick(self) -> None:
        self._addExpressionToHistory()
        self._calculateCurrentExpression()

    def _setExpressionFromHistory(self) -> None:
        expr = self.history_list_view.currentIndex().data(Qt.UserRole)
        self.entry_field.setText(expr)

    def resizeEvent(self, event: QResizeEvent) -> None:
        pass

    def keyPressEvent(self, event: QKeyEvent) -> None:
        index = self.history_list_view.currentIndex()

        if event.matches(QKeySequence.Cut):
            self._cutSelectedEquation(index)

    def contextMenu(self, pos: QPoint) -> None:
        menu = QMenu()
        index = self.history_list_view.currentIndex()

        if index.row() >= 0:
            copy_equation = menu.addAction('Copy equation')
            cut_equation = menu.addAction('Cut equation')
            copy_expression = menu.addAction('Copy expression')
            edit_expression = menu.addAction('Edit expression')
            delete = menu.addAction('Delete')
            action = menu.exec_(self.history_list_view.mapToGlobal(pos))

            if action == delete:
                self._deleteSelectedEquation(index)
            elif action == copy_equation:
                self._copySelectedEquation(index)
            elif action == copy_expression:
                self._copySelectedExpression(index)
            elif action == cut_equation:
                self._cutSelectedEquation(index)
            elif action == edit_expression:
                self._editSelectedExpression(index)
        else:
            clear_history = menu.addAction('Clear history')
            save_history = menu.addAction('Save history')
            action = menu.exec_(self.history_list_view.mapToGlobal(pos))

            if action == save_history:
                self._saveHistoryButton()
            elif action == clear_history:
                self._clearHistoryButton()
