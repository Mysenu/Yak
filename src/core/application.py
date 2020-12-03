from typing import List, Optional

from PyQt5.QtWidgets import QApplication

from src.ui import MainWindow


class Application(QApplication):
    def __init__(self, args: Optional[List] = None) -> None:
        super().__init__(args or [])

        self.main_window = MainWindow()
        self.main_window.show()
