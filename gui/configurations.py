from PyQt5.QtCore import QObject, QRect
from PyQt5.QtWidgets import (QDialog, QGroupBox, QLineEdit, QPushButton)

# This boolean is used to keep track of which of the two Hostname or Network
# window to display.
# By default, the Hostname window is displayed to the user.
# It is possible to switch the mode by clicking the right push buttons.
# When configuring another device, the chosen mode will be remembered.
NETWORK_MODE = False

# These constants are initialised within init_config_windows
HOSTNAME_WINDOW = None
NETWORK_WINDOW = None


def init_config_windows():
    """This function must be called at the Qt application initialisation"""
    global HOSTNAME_WINDOW, NETWORK_WINDOW
    HOSTNAME_WINDOW = HostnameWindow()
    NETWORK_WINDOW = NetworkWindow()


def display_config_window():
    if NETWORK_MODE:
        if HOSTNAME_WINDOW.parent.isVisible():
            HOSTNAME_WINDOW.parent.close()
        if not NETWORK_WINDOW.parent.isVisible():
            NETWORK_WINDOW.parent.show()
    else:
        if NETWORK_WINDOW.parent.isVisible():
            NETWORK_WINDOW.parent.close()
        if not HOSTNAME_WINDOW.parent.isVisible():
            HOSTNAME_WINDOW.parent.show()


class HostnameWindow(QObject):
    """HostnameWindow only allows the setting of a device's hostname.

    Setting the hostname is the most common operation, and is ipassign's
    default mode of operation.
    """

    def __init__(self, parent=None):
        super(HostnameWindow, self).__init__(parent=parent)
        if parent is None:
            parent = QDialog()
        parent.setObjectName('hostnameProperty')
        parent.setWindowTitle('ICEPAP Parameters & Configuration')
        parent.setModal(False)
        parent.resize(380, 150)
        self.parent = parent

        gbHostname = QGroupBox(parent)
        gbHostname.setObjectName('gbHostname')
        gbHostname.setTitle('Hostname')
        gbHostname.setGeometry(QRect(50, 10, 280, 60))

        leHostname = QLineEdit(gbHostname)
        leHostname.setObjectName('leHostname')
        leHostname.setGeometry(QRect(10, 23, 260, 30))

        pbNetworkMode = QPushButton(parent)
        pbNetworkMode.setObjectName('pbNetworkMode')
        pbNetworkMode.setText('Advanced')
        pbNetworkMode.setGeometry(QRect(10, 90, 80, 40))
        pbNetworkMode.clicked.connect(self.switch_mode)

        pbApply = QPushButton(parent)
        pbApply.setObjectName('pbApply')
        pbApply.setText('Apply')
        pbApply.setGeometry(QRect(180, 90, 80, 40))

        pbCancel = QPushButton(parent)
        pbCancel.setObjectName('pbCancel')
        pbCancel.setText('Cancel')
        pbCancel.setGeometry(QRect(270, 90, 80, 40))
        pbCancel.clicked.connect(parent.close)

    def switch_mode(self):
        global NETWORK_MODE
        NETWORK_MODE = True
        display_config_window()


class NetworkWindow(QObject):
    """NetworkWindow allows the setting of all of a device's network settings.
    """

    def __init__(self, parent=None):
        super(NetworkWindow, self).__init__(parent=parent)
        if parent is None:
            parent = QDialog()
        parent.setObjectName('networkProperties')
        parent.setWindowTitle('ICEPAP Parameters & Configuration')
        parent.setModal(False)
        parent.resize(630, 430)
        self.parent = parent

        pbHostnameMode = QPushButton(parent)
        pbHostnameMode.setObjectName('pbHostnameMode')
        pbHostnameMode.setText('Simple Mode')
        pbHostnameMode.setGeometry(QRect(20, 370, 116, 40))
        pbHostnameMode.clicked.connect(self.switch_mode)

        pbCancel = QPushButton(parent)
        pbCancel.setObjectName('pbCancel')
        pbCancel.setText('Cancel')
        pbCancel.setGeometry(QRect(490, 370, 116, 40))
        pbCancel.clicked.connect(parent.close)

    def display(self):
        if not self.parent.isVisible():
            self.parent.show()

    def switch_mode(self):
        global NETWORK_MODE
        NETWORK_MODE = False
        display_config_window()
