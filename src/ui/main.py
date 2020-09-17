import sys

from PyQt5.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def my_excepthook(type, value, tback):
    sys.__excepthook__(type, value, tback)


sys.excepthook = my_excepthook
app = QApplication(sys.argv)

window = MainWindow()
exit(app.exec_())
