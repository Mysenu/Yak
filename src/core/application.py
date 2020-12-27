from typing import List, Optional

from PyQt5.QtWidgets import QApplication, QMessageBox

from src.history.utils import readHistoryCache, clearHistoryCache
from src.ui import MainWindow


class Application(QApplication):
    def __init__(self, args: Optional[List] = None) -> None:
        super().__init__(args or [])

        self.main_window = MainWindow()
        self.main_window.show()

        self.addHistoryCacheToHistory(self.needToRestoreHistory())

    def needToRestoreHistory(self) -> bool:
        answer = QMessageBox.question(MainWindow(), 'Restore history', 'Restore calculation history?')
        return answer == QMessageBox.Yes

    def addHistoryCacheToHistory(self, answer: bool) -> None:
        if answer:
            expressions = readHistoryCache()
            if expressions:
                self.main_window.history_list_model.addExpressions(expressions)
        else:
            clearHistoryCache()
