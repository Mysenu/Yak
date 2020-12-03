import sys

from src.core.application import Application

from src.ui.main_window import MainWindow


def my_excepthook(type, value, tback) -> None:
    sys.__excepthook__(type, value, tback)


def main() -> int:
    sys.excepthook = my_excepthook
    app = Application(sys.argv)
    return app.exec_()


if __name__ == '__main__':
    exit(main())
