from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, qApp, QSizePolicy, QGridLayout, QSplitter

from src.expression import calculateExpr
from src.history import HistoryListModel, HistoryListView
from src.history import ExpressionRole
from .button import Button
from .expression_field import ExpressionField


class MainWindow(QSplitter):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setWindowTitle('Calculator')
        self.resize(600, 400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        font = self.font()
        font.setFamily('monospace [Consolas]')
        self.setFont(font)

        # Калькулятор
        calc_widget = QWidget()
        self.addWidget(calc_widget)

        calc_layout = QVBoxLayout(calc_widget)
        calc_layout.setContentsMargins(4, 4, 4, 4)
        calc_layout.setSpacing(4)

        # Поле ввода
        self.entry_field = ExpressionField()
        self.entry_field.returnPressed.connect(self._onEvalButtonClick)
        calc_layout.addWidget(self.entry_field)

        # Кнопки калькулятора
        action_layout = QGridLayout()
        calc_layout.addLayout(action_layout)

        self.clean_entry_button = Button('C', self.entry_field.clear)
        action_layout.addWidget(self.clean_entry_button, 0, 0)

        self.backspace_button = Button('⌫', self.entry_field.backspace)
        action_layout.addWidget(self.backspace_button, 0, 1)

        self.power_button = Button('^', self._onButtonClick)
        action_layout.addWidget(self.power_button, 0, 2)

        self.square_root_button = Button('√', self._onButtonClick)
        action_layout.addWidget(self.square_root_button, 0, 3)

        # Вторая строка
        self.open_bracket_button = Button('(', self._onButtonClick)
        action_layout.addWidget(self.open_bracket_button, 1, 0)

        self.close_bracket_button = Button(')', self._onButtonClick)
        action_layout.addWidget(self.close_bracket_button, 1, 1)

        self.percent_button = Button('%', self._onButtonClick)
        action_layout.addWidget(self.percent_button, 1, 2)

        self.division_button = Button('÷', self._onButtonClick)
        action_layout.addWidget(self.division_button, 1, 3)

        # Третья строка
        self.seven_button = Button('7', self._onButtonClick)
        action_layout.addWidget(self.seven_button, 2, 0)

        self.eight_button = Button('8', self._onButtonClick)
        action_layout.addWidget(self.eight_button, 2, 1)

        self.nine_button = Button('9', self._onButtonClick)
        action_layout.addWidget(self.nine_button, 2, 2)

        self.multiplication_button = Button('×', self._onButtonClick)
        action_layout.addWidget(self.multiplication_button, 2, 3)

        # Четвертая строка
        self.four_button = Button('4', self._onButtonClick)
        action_layout.addWidget(self.four_button, 3, 0)

        self.five_button = Button('5', self._onButtonClick)
        action_layout.addWidget(self.five_button, 3, 1)

        self.six_button = Button('6', self._onButtonClick)
        action_layout.addWidget(self.six_button, 3, 2)

        self.minus_button = Button('–', self._onButtonClick)
        action_layout.addWidget(self.minus_button, 3, 3)

        # Пятая строка
        self.one_button = Button('1', self._onButtonClick)
        action_layout.addWidget(self.one_button, 4, 0)

        self.two_button = Button('2', self._onButtonClick)
        action_layout.addWidget(self.two_button, 4, 1)

        self.three_button = Button('3', self._onButtonClick)
        action_layout.addWidget(self.three_button, 4, 2)

        self.plus_button = Button('+', self._onButtonClick)
        action_layout.addWidget(self.plus_button, 4, 3)

        # Шестая строка
        self.zero_button = Button('0', self._onButtonClick)
        action_layout.addWidget(self.zero_button, 5, 0, 1, 2)

        self.dot_button = Button('.', self._onButtonClick)
        action_layout.addWidget(self.dot_button, 5, 2)

        self.result_button = Button('=', self._onEvalButtonClick)
        action_layout.addWidget(self.result_button, 5, 3)

        # История
        self.history_list_model = HistoryListModel()
        self.history_list_view = HistoryListView()
        self.history_list_view.setModel(self.history_list_model)

        self.addWidget(self.history_list_view)

    def _onButtonClick(self) -> None:
        char_to_add = qApp.sender().text()
        self.entry_field.insert(char_to_add)

    def _calculateCurrentExpression(self) -> None:
        result = calculateExpr(self.entry_field.text())
        if result is not None:
            self.entry_field.setText(str(result))

    def _addExpressionToHistory(self) -> None:
        expr = self.entry_field.text()
        self.history_list_model.addExpression(expr)

    def _onEvalButtonClick(self) -> None:
        self._addExpressionToHistory()
        self._calculateCurrentExpression()

    def _setExpressionFromHistory(self) -> None:
        expr = self.history_list_view.currentIndex().data(ExpressionRole)
        self.entry_field.setText(expr)
