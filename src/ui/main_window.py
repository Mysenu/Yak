from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, qApp, QSizePolicy, QGridLayout, QSplitter

from src.expression import calculateExpr
from src.history import HistoryListModel, HistoryListView
from src.history import ExpressionRole
from .button import Button
from .expression_field import ExpressionField


MINIMUM_WINDOW_WIDTH = 80
MINIMUM_WINDOW_HEIGHT = 175


class MainWindow(QSplitter):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setWindowTitle('Calculator')
        self.resize(450, 300)
        self.setMinimumSize(MINIMUM_WINDOW_WIDTH, MINIMUM_WINDOW_HEIGHT)

        font = self.font()
        font.setFamily('Consolas')
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        self._no_history = False
        self._one_widget = False

        # Калькулятор
        calc_widget = QWidget()
        self.addWidget(calc_widget)

        calc_layout = QVBoxLayout(calc_widget)
        calc_layout.setContentsMargins(4, 4, 4, 4)
        calc_layout.setSpacing(4)
        calc_widget.setMinimumSize(MINIMUM_WINDOW_WIDTH, MINIMUM_WINDOW_HEIGHT)
        calc_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

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
        self.history_list_view.setMinimumSize(MINIMUM_WINDOW_WIDTH, MINIMUM_WINDOW_HEIGHT)

        self.addWidget(self.history_list_view)

        self.history_list_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.setHandleWidth(1)
        self.setStretchFactor(0, 5)
        self.setStretchFactor(1, 5)

    def _onButtonClick(self) -> None:
        button = qApp.sender()
        self.entry_field.insert({
            self.power_button: '^',
            self.square_root_button: 'V',
            self.percent_button: '%',
            self.division_button: '/',
            self.multiplication_button: '*',
            self.plus_button: '+',
            self.minus_button: '-',
            self.one_button: '1',
            self.two_button: '2',
            self.three_button: '3',
            self.four_button: '4',
            self.five_button: '5',
            self.six_button: '6',
            self.seven_button: '7',
            self.eight_button: '8',
            self.nine_button: '9',
            self.zero_button: '0',
            self.dot_button: '.',
            self.open_bracket_button: '(',
            self.close_bracket_button: ')'
                                }[button])

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

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        self.entry_field.setFixedHeight(int(self.height() * 0.13))  # 50 / 380 (entry_field.height / MainWindow.height)
        font = self.font()
        font.setPointSize(self.height() * 0.13 * 0.4)
        self.history_list_view.setFont(font)

        minimum_window_size_to_change = MINIMUM_WINDOW_WIDTH * 4  # Twice the size of the minimum size of the window
        calc_size, history_size = self.sizes()
        if not self._one_widget:
            if self.width() < minimum_window_size_to_change:
                if not self._no_history:
                    self.setSizes([1, 0])
                    self._no_history = True

                if calc_size == 0:
                    self._one_widget = True
                    self._no_history = False

            elif self.width() > minimum_window_size_to_change:
                if self._no_history:
                    self.setSizes([1, 1])
                    self._no_history = False

        if not self._no_history:
            if calc_size == 0 or history_size == 0:
                self._one_widget = True
            else:
                self._one_widget = False

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if not event.matches(QKeySequence.InsertParagraphSeparator):
            self.entry_field.keyPressEvent(event)
