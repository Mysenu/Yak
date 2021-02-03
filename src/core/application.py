from typing import List, Optional

from PyQt5.QtWidgets import QApplication, QMessageBox

from src.core.utils import getResourcePath
from src.ui import MainWindow
from src.ui.history import loadHistoryFromCache, CACHE_FILE


class Application(QApplication):
    def __init__(self, args: Optional[List] = None) -> None:
        super().__init__(args or [])

        self.main_window = MainWindow()

        if self.needToRestoreHistory():
            self.addHistoryCacheToHistory()

        with open(getResourcePath("main.qss"), 'r', encoding='utf-8') as file_with_style_sheet:
            self.setStyleSheet(file_with_style_sheet.read())

        self.main_window.show()

    def needToRestoreHistory(self) -> bool:
        if not CACHE_FILE.exists() or (CACHE_FILE.stat().st_size <= 0):
            return False

        answer = QMessageBox.question(self.main_window, 'Restore history', 'Restore calculation history?')
        return answer == QMessageBox.Yes

    def addHistoryCacheToHistory(self) -> None:
        expressions = loadHistoryFromCache()
        if expressions:
            self.main_window.history_list_model.addExpressions(expressions)
