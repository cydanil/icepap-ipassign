import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from .configurations import init_config_windows
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

    hostname, network = init_config_windows()

    hostname.done.connect(main.list_devices)
    network.done.connect(main.list_devices)
    main.pbLog.clicked.connect(log.display)
    main.list_devices()

    w.show()
    log.log('Launched')
    sys.exit(app.exec_())
