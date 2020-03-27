import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from .configurations import display_config_window, init_config_windows
from .logwindow import LogWindow
from .mainwindow import MainWindow


def main():
    """The application's entry point.

    After creating the Qt application, this will automatically look for
    device's on the network, and list them within the main window.
    """
    app = QApplication(sys.argv)

    w = QMainWindow()
    main = MainWindow(w)
    log = LogWindow()

    init_config_windows()

    main.pbLog.clicked.connect(log.display)
    main.pbProperties.clicked.connect(display_config_window)

    w.show()
    log.log('Launched')
    sys.exit(app.exec_())
