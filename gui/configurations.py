from ipassign.utils import validate_ip_addr

from PyQt5.QtCore import QObject, QRect, Qt
from PyQt5.QtWidgets import (QCheckBox, QDialog,
                             QGroupBox, QLineEdit, QPushButton)

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
        pbApply.clicked.connect(self.apply)

        pbCancel = QPushButton(parent)
        pbCancel.setObjectName('pbCancel')
        pbCancel.setText('Cancel')
        pbCancel.setGeometry(QRect(270, 90, 80, 40))
        pbCancel.clicked.connect(parent.close)

    def switch_mode(self):
        global NETWORK_MODE
        NETWORK_MODE = True
        display_config_window()

    def apply(self):
        print('kthxbye')


class NetworkWindow(QObject):
    """NetworkWindow allows the setting of all of a device's network settings.

    These are Hostname, IP settings, and whether to apply these settings
    dynamically, write them to flash, or reboot.

    Alternatively, it is also possible to query the DNS and set these as values
    to apply.

    There is also a button to re-query the device for its current settings.
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

        # mac address display
        gbMac = QGroupBox(parent)
        gbMac.setObjectName('gbMac')
        gbMac.setTitle('MAC address')
        gbMac.setGeometry(QRect(190, 10, 250, 60))

        leMac = QLineEdit(gbMac)
        leMac.setObjectName('leMac')
        leMac.setGeometry(QRect(10, 25, 230, 30))
        leMac.setAlignment(Qt.AlignHCenter)
        leMac.setReadOnly(True)
        leMac.setText('00:DE:AD:BE:EF')

        # ip setting
        gbIP = QGroupBox(parent)
        gbIP.setObjectName('gbIP')
        gbIP.setTitle('IP address')
        gbIP.setGeometry(QRect(20, 80, 250, 60))

        leIP = QLineEdit(gbIP)
        leIP.setObjectName('leIP1')
        leIP.setGeometry(QRect(10, 25, 230, 30))
        leIP.textChanged.connect(self.validate_ip)
        leIP.textChanged.emit(leIP.text())

        # netmask setting
        gbNetmask = QGroupBox(parent)
        gbNetmask.setObjectName('gbNetmask')
        gbNetmask.setTitle('Netmask address')
        gbNetmask.setGeometry(QRect(20, 150, 250, 60))

        leNetmask = QLineEdit(gbNetmask)
        leNetmask.setObjectName('leNetmask1')
        leNetmask.setGeometry(QRect(10, 25, 230, 30))
        leNetmask.textChanged.connect(self.validate_ip)
        leNetmask.textChanged.emit(leNetmask.text())

        # gateway setting
        gbGateway = QGroupBox(parent)
        gbGateway.setObjectName('gbGateway')
        gbGateway.setTitle('Gateway address')
        gbGateway.setGeometry(QRect(20, 220, 250, 60))

        leGateway = QLineEdit(gbGateway)
        leGateway.setObjectName('leGateway1')
        leGateway.setGeometry(QRect(10, 25, 230, 30))
        leGateway.textChanged.connect(self.validate_ip)
        leGateway.textChanged.emit(leGateway.text())

        # broadcast setting
        gbBroadcast = QGroupBox(parent)
        gbBroadcast.setObjectName('gbBroadcast')
        gbBroadcast.setTitle('Broadcast address')
        gbBroadcast.setGeometry(QRect(20, 290, 250, 60))

        leBroadcast = QLineEdit(gbBroadcast)
        leBroadcast.setObjectName('leBroadcast1')
        leBroadcast.setGeometry(QRect(10, 25, 230, 30))
        leBroadcast.textChanged.connect(self.validate_ip)
        leBroadcast.textChanged.emit(leBroadcast.text())

        # hostname setting
        gbHostname = QGroupBox(parent)
        gbHostname.setObjectName('gbHostname')
        gbHostname.setTitle('Hostname')
        gbHostname.setGeometry(QRect(330, 80, 250, 60))

        leHostname = QLineEdit(gbHostname)
        leHostname.setObjectName('leHostname1')
        leHostname.setGeometry(QRect(10, 25, 230, 30))
        leHostname.textChanged.connect(self.validate_ip)
        leHostname.textChanged.emit(leHostname.text())

        # apply and commands settings
        gbApply = QGroupBox(parent)
        gbApply.setObjectName('gbApply')
        gbApply.setTitle('Options')
        gbApply.setGeometry(QRect(360, 150, 220, 200))

        cbDynamic = QCheckBox(gbApply)
        cbDynamic.setObjectName('cbDynamic')
        cbDynamic.setText('Dynamic')
        cbDynamic.setGeometry(QRect(20, 30, 160, 20))
        cbDynamic.setToolTip('Apply immediately, whitout reboot')

        cbFlash = QCheckBox(gbApply)
        cbFlash.setObjectName('cbFlash')
        cbFlash.setText('Write to Flash')
        cbFlash.setGeometry(QRect(20, 60, 160, 20))
        cbFlash.setToolTip("Write settings to the device's flash")

        cbReboot = QCheckBox(gbApply)
        cbReboot.setObjectName('cbReboot')
        cbReboot.setText('Reboot')
        cbReboot.setGeometry(QRect(20, 90, 160, 20))
        cbReboot.setToolTip('Reboot after applying the settings')

        pbApply = QPushButton(gbApply)
        pbApply.setObjectName('pbApply')
        pbApply.setText('Apply')
        pbApply.setGeometry(QRect(90, 145, 116, 40))
        pbApply.setToolTip('Send the configuration to the device')
        pbApply.clicked.connect(self.apply)

        # other actions
        pbHostnameMode = QPushButton(parent)
        pbHostnameMode.setObjectName('pbHostnameMode')
        pbHostnameMode.setText('Simple Mode')
        pbHostnameMode.setGeometry(QRect(20, 370, 116, 40))
        pbHostnameMode.clicked.connect(self.switch_mode)

        pbQueryDNS = QPushButton(parent)
        pbQueryDNS.setObjectName('pbQueryDNS')
        pbQueryDNS.setText('Set DNS values')
        pbQueryDNS.setGeometry(QRect(170, 370, 116, 40))
        pbQueryDNS.clicked.connect(self.query_dns)

        tip = ('If the hostname is found in the DNS, then the values from the '
               'DNS will be loaded, but not applied')
        pbQueryDNS.setToolTip(tip)

        pbQueryDevice = QPushButton(parent)
        pbQueryDevice.setObjectName('pbQueryDevice')
        pbQueryDevice.setText('Read HW values')
        pbQueryDevice.setGeometry(QRect(350, 370, 116, 40))
        pbQueryDevice.setToolTip('Re-query the device, and load its values')
        pbQueryDevice.clicked.connect(self.query_device)

        pbCancel = QPushButton(parent)
        pbCancel.setObjectName('pbCancel')
        pbCancel.setText('Cancel')
        pbCancel.setGeometry(QRect(490, 370, 116, 40))
        pbCancel.clicked.connect(parent.close)

    def validate_ip(self):
        sender = self.sender()
        content = sender.text()
        color = '#f6989d'  # red
        if content.count('.') == 3:
            ok, _ = validate_ip_addr(content)
            if ok:
                color = '#c4df9b'  # green
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

    def switch_mode(self):
        global NETWORK_MODE
        NETWORK_MODE = False
        display_config_window()

    def query_dns(self):
        print('query dns')

    def query_device(self):
        print('query device')

    def apply(self):
        print('kthxbye')
        self.parent.close()
