import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from .mainwindow import MainWindow
from .logwindow import LogWindow


def ipassign():
    app = QApplication(sys.argv)

    w = QMainWindow()
    main = MainWindow(w)
    log = LogWindow()

    main.pbLog.clicked.connect(log.display)

    w.show()
    log.log('Launched')
    sys.exit(app.exec_())


if __name__ == '__main__':
    ipassign()
