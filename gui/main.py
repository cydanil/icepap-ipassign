import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from .configurations import init_config_windows
from .logwindow import LogWindow
from .mainwindow import MainWindow
from .networking import network


def main():
    """The application's entry point.

    After creating the Qt application, this will automatically look for
    device's on the network, and list them within the main window.
    """

    app = QApplication(sys.argv)

    window = QMainWindow()
    main_window = MainWindow(window)
    hm_window, nw_window = init_config_windows()
    log = LogWindow()

    hm_window.done.connect(main_window.list_devices)
    nw_window.done.connect(main_window.list_devices)

    network.log.connect(log.log)
    hm_window.log.connect(log.log)
    nw_window.log.connect(log.log)

    main_window.pbLog.clicked.connect(log.display)

    window.show()

    log.log('Launched')
    main_window.list_devices()

    sys.exit(app.exec_())
