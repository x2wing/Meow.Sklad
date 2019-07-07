from PyQt5 import QtWidgets
from widgets.main_window import MainWindow


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    main = MainWindow()

    main.show()

    app.exec()