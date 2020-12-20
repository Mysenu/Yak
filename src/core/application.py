from typing import List, Optional

from PyQt5.QtWidgets import QApplication, QMessageBox

from src.history.utils import readHistoryCacheFile, CACHE_DIR
from src.ui import MainWindow


class Application(QApplication):
    def __init__(self, args: Optional[List] = None) -> None:
        super().__init__(args or [])

        self.main_window = MainWindow()
        self.main_window.show()

        self.addHistoryCacheToHistory(self.restoreHistory())

    def restoreHistory(self) -> QMessageBox:
        return QMessageBox.question(MainWindow(), 'Restore history', 'Restore calculation history?')

    def addHistoryCacheToHistory(self, restore_history: QMessageBox) -> None:
        if restore_history == QMessageBox.Yes:
            expressions = readHistoryCacheFile()
            if expressions:
                self.main_window.history_list_model.addExpressions(expressions)
        else:
            open(CACHE_DIR / 'calc', 'w').close()
