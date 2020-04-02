import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from .configurations import init_config_windows
from .logwindow import LogWindow
from .mainwindow import MainWindow
from .networking import network


def main():
    """The application's entry point.

    This creates the Qt application, and connects all slots and signals.
    After that, it will automatically look for device's on the network, and
    list them within the main window.
    """

    app = QApplication(sys.argv)

    window = QMainWindow()
    main_window = MainWindow(window)

    # Initalise the configuration windows.
    # These are not directly connected to the main window, as the main window
    # uses a handler to handle switching modes.
    hm_window, nw_window = init_config_windows()

    log = LogWindow()
    main_window.pbLog.clicked.connect(log.display)

    # Connect the configuration windows to trigger re-discoveries upon
    # reconfiguring a device.
    hm_window.done.connect(main_window.list_devices)
    nw_window.done.connect(main_window.list_devices)

    # Connect the various windows to send log message to the logger.
    network.log.connect(log.log)
    hm_window.log.connect(log.log)
    nw_window.log.connect(log.log)

    # Display the main window, through its parent.
    window.show()

    log.log('Launched')
    main_window.list_devices()

    sys.exit(app.exec_())
