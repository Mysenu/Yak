from typing import List, Optional

from PyQt5.QtWidgets import QApplication, QMessageBox

from src.history.utils import loadHistoryFromCache, clearHistoryCache, CACHE_FILE
from src.ui import MainWindow
from src.ui.utils import getResourcePath


class Application(QApplication):
    def __init__(self, args: Optional[List] = None) -> None:
        super().__init__(args or [])

        self.main_window = MainWindow()

        if (CACHE_FILE.exists() and (CACHE_FILE.stat().st_size > 0)) and self.needToRestoreHistory():
            self.addHistoryCacheToHistory()

        with open(getResourcePath("main.qss"), 'r', encoding='utf-8') as style_sheet:
            self.setStyleSheet(style_sheet.read())
            
        self.main_window.show()

    def needToRestoreHistory(self) -> bool:
        answer = QMessageBox.question(self.main_window, 'Restore history', 'Restore calculation history?')
        return answer == QMessageBox.Yes

    def addHistoryCacheToHistory(self) -> None:
        expressions = loadHistoryFromCache()
        if expressions:
            self.main_window.history_list_model.addExpressions(expressions)
