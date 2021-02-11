from typing import List, Optional

from PyQt5.QtWidgets import QApplication, QMessageBox, QCheckBox
from PyQt5.QtCore import Qt, QSettings

from src.core.utils import getResourcePath
from src.ui import MainWindow
from src.ui.history import loadHistoryFromCache, CACHE_FILE


class Application(QApplication):
    def __init__(self, args: Optional[List] = None) -> None:
        super().__init__(args or [])

        self.main_window = MainWindow()

        self._setting = QSettings('Egor', 'YAK')

        with open(getResourcePath("main.qss"), 'r', encoding='utf-8') as file_with_style_sheet:
            self.setStyleSheet(file_with_style_sheet.read())

        if not self._setting.value('dont_show_again') and self.needToRestoreHistory():
            self.addHistoryCacheToHistory()

        self.main_window.show()

    def needToRestoreHistory(self) -> bool:
        if not CACHE_FILE.exists() or (CACHE_FILE.stat().st_size <= 0):
            return False

        dont_show_checkbox = QCheckBox('Don`t show again')

        message = QMessageBox(self.main_window)
        message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message.setWindowTitle('Restore history')
        message.setText('Restore calculation history?')
        message.setCheckBox(dont_show_checkbox)
        message.setIcon(QMessageBox.Question)

        answer = message.exec()

        if dont_show_checkbox.checkState() == Qt.Checked:
            self._setting.setValue('dont_show_again', 1)
            self.main_window.history_list_view.statusRestoreHistory()
        return answer == QMessageBox.Yes

    def addHistoryCacheToHistory(self) -> None:
        expressions = loadHistoryFromCache()
        if expressions:
            self.main_window.history_list_model.addExpressions(expressions)
