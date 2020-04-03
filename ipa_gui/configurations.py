import string

from PyQt5.QtCore import pyqtSignal, QObject, QRect, Qt
from PyQt5.QtWidgets import (QCheckBox, QDialog, QGroupBox,
                             QLineEdit, QMessageBox, QPushButton)

from ipassign.utils import validate_ip_addr
from ipassign import Configuration, acknowledgements

from .networking import gethostbyname, network

# These are used to validate hostnames
VALID_HN_CHARS = string.ascii_letters + string.digits + '-'

# These colours are used in validators to highlight the QLineEdits
RED = '#f6989d'
GREEN = '#c4df9b'

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
    return HOSTNAME_WINDOW, NETWORK_WINDOW


def display_config_window(config: Configuration = None) -> None:
    if NETWORK_MODE:
        if HOSTNAME_WINDOW.parent.isVisible():
            HOSTNAME_WINDOW.parent.close()
        if not NETWORK_WINDOW.parent.isVisible():
            NETWORK_WINDOW.show(config)
    else:
        if NETWORK_WINDOW.parent.isVisible():
            NETWORK_WINDOW.parent.close()
        if not HOSTNAME_WINDOW.parent.isVisible():
            HOSTNAME_WINDOW.show(config)


class HostnameWindow(QObject):
    """HostnameWindow only allows the setting of a device's hostname.

    Setting the hostname is the most common operation, and is ipassign's
    default mode of operation.
    """

    done = pyqtSignal()
    log = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        if parent is None:
            parent = QDialog()

        parent.setObjectName('hostnameProperty')
        parent.setWindowTitle('IcePAP Parameters & Configuration')
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
        leHostname.setToolTip(f'Valid characters are {VALID_HN_CHARS}')
        leHostname.textChanged.connect(self.validator)
        leHostname.textChanged.emit(leHostname.text())
        self.leHostname = leHostname

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
        pbApply.setEnabled(False)
        self.pbApply = pbApply

        pbCancel = QPushButton(parent)
        pbCancel.setObjectName('pbCancel')
        pbCancel.setText('Cancel')
        pbCancel.setGeometry(QRect(270, 90, 80, 40))
        pbCancel.clicked.connect(parent.close)

        self._config = None

    def validator(self):
        sender = self.sender()
        content = sender.text()
        color = RED

        if hasattr(self, 'pbApply'):
            self.pbApply.setEnabled(False)

        if (content and all([c in VALID_HN_CHARS for c in content])
                and not content.startswith('-')):
            color = GREEN

        if color is GREEN:
            self.pbApply.setEnabled(True)
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

    def show(self, config: Configuration) -> None:
        self._config = config
        self.leHostname.setText(config.hostname)
        self.parent.show()

    def switch_mode(self):
        self._config.hostname = self.leHostname.text()
        config, self._config = self._config, None
        global NETWORK_MODE
        NETWORK_MODE = True
        display_config_window(config)

    def apply(self):
        hostname = self.leHostname.text()
        self.log.emit(f'Renaming {self._config.hostname} -> {hostname}')
        self._config.hostname = hostname
        config, self._config = self._config, None
        self.parent.close()

        ret = network.send_configuration(config)
        msg = f'{config.mac} ({config.hostname}) '
        if ret is None:
            msg += 'did not send an acknowledgment in time!'
            QMessageBox.warning(self.parent, 'No acknowledgement!', msg)
        elif ret is acknowledgements.OK:
            msg += 'applied config ok'
            QMessageBox.information(self.parent, 'Device reply', msg)
        else:
            msg += 'replied with {ret.name} {ret.value}]'
            QMessageBox.warning(self.parent, 'Error on device!', msg)

        self.done.emit()


class NetworkWindow(QObject):
    """NetworkWindow allows the setting of all of a device's network settings.

    These are Hostname, IP settings, and whether to apply these settings
    dynamically, to write them to flash, or reboot.

    Alternatively, it is also possible to query the DNS and set these as values
    to apply.

    The configuration given at the moment of drawing the window is kept
    within `self._config`.

    The new configuration will only be created when `self.pbApply` is clicked.
    """

    done = pyqtSignal()
    log = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        if parent is None:
            parent = QDialog()
        parent.setObjectName('networkProperties')
        parent.setWindowTitle('IcePAP Parameters & Configuration')
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
        self.leMac = leMac

        # ip setting
        gbIP = QGroupBox(parent)
        gbIP.setObjectName('gbIP')
        gbIP.setTitle('IP address')
        gbIP.setGeometry(QRect(20, 80, 250, 60))

        leIP = QLineEdit(gbIP)
        leIP.setObjectName('leIP1')
        leIP.setGeometry(QRect(10, 25, 230, 30))
        leIP.textChanged.connect(self.validator)
        leIP.textChanged.emit(leIP.text())
        self.leIP = leIP

        # netmask setting
        gbNetmask = QGroupBox(parent)
        gbNetmask.setObjectName('gbNetmask')
        gbNetmask.setTitle('Netmask address')
        gbNetmask.setGeometry(QRect(20, 150, 250, 60))

        leNetmask = QLineEdit(gbNetmask)
        leNetmask.setObjectName('leNetmask1')
        leNetmask.setGeometry(QRect(10, 25, 230, 30))
        leNetmask.textChanged.connect(self.validator)
        leNetmask.textChanged.emit(leNetmask.text())
        self.leNetmask = leNetmask

        # gateway setting
        gbGateway = QGroupBox(parent)
        gbGateway.setObjectName('gbGateway')
        gbGateway.setTitle('Gateway address')
        gbGateway.setGeometry(QRect(20, 220, 250, 60))

        leGateway = QLineEdit(gbGateway)
        leGateway.setObjectName('leGateway1')
        leGateway.setGeometry(QRect(10, 25, 230, 30))
        leGateway.textChanged.connect(self.validator)
        leGateway.textChanged.emit(leGateway.text())
        self.leGateway = leGateway

        # broadcast setting
        gbBroadcast = QGroupBox(parent)
        gbBroadcast.setObjectName('gbBroadcast')
        gbBroadcast.setTitle('Broadcast address')
        gbBroadcast.setGeometry(QRect(20, 290, 250, 60))

        leBroadcast = QLineEdit(gbBroadcast)
        leBroadcast.setObjectName('leBroadcast1')
        leBroadcast.setGeometry(QRect(10, 25, 230, 30))
        leBroadcast.textChanged.connect(self.validator)
        leBroadcast.textChanged.emit(leBroadcast.text())
        self.leBroadcast = leBroadcast

        # hostname setting
        gbHostname = QGroupBox(parent)
        gbHostname.setObjectName('gbHostname')
        gbHostname.setTitle('Hostname')
        gbHostname.setGeometry(QRect(330, 80, 250, 60))

        leHostname = QLineEdit(gbHostname)
        leHostname.setObjectName('leHostname1')
        leHostname.setGeometry(QRect(10, 25, 230, 30))
        leHostname.setToolTip(f'Valid characters are {VALID_HN_CHARS}')
        leHostname.textChanged.connect(self.validator)
        leHostname.textChanged.emit(leHostname.text())
        self.leHostname = leHostname

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
        self.cbDynamic = cbDynamic

        cbFlash = QCheckBox(gbApply)
        cbFlash.setObjectName('cbFlash')
        cbFlash.setText('Write to Flash')
        cbFlash.setGeometry(QRect(20, 60, 160, 20))
        cbFlash.setToolTip("Write settings to the device's flash")
        self.cbFlash = cbFlash

        cbReboot = QCheckBox(gbApply)
        cbReboot.setObjectName('cbReboot')
        cbReboot.setText('Reboot')
        cbReboot.setGeometry(QRect(20, 90, 160, 20))
        cbReboot.setToolTip('Reboot after applying the settings')
        self.cbReboot = cbReboot

        pbApply = QPushButton(gbApply)
        pbApply.setObjectName('pbApply')
        pbApply.setText('Apply')
        pbApply.setGeometry(QRect(90, 145, 116, 40))
        pbApply.setToolTip('Send the configuration to the device')
        pbApply.clicked.connect(self.apply)
        self.pbApply = pbApply

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

        tip = ('If the hostname is found in the DNS, then the ip address from '
               'the DNS will be loaded, but not applied')
        pbQueryDNS.setToolTip(tip)

        pbReset = QPushButton(parent)
        pbReset.setObjectName('pbReset')
        pbReset.setText('Reset')
        pbReset.setGeometry(QRect(350, 370, 116, 40))
        pbReset.setToolTip('Load values obtained from device')
        pbReset.clicked.connect(self.reset)

        pbCancel = QPushButton(parent)
        pbCancel.setObjectName('pbCancel')
        pbCancel.setText('Cancel')
        pbCancel.setGeometry(QRect(490, 370, 116, 40))
        pbCancel.clicked.connect(parent.close)

        self.config = None

    def validator(self):
        sender = self.sender()
        content = sender.text()
        ok = False
        color = RED

        if hasattr(self, 'pbApply'):
            self.pbApply.setEnabled(False)

        if 'leHostname' in sender.objectName():
            if (content and all([c in VALID_HN_CHARS for c in content])
                    and not content.startswith('-')):
                ok = True
        else:  # it's an IP address string
            if content.count('.') == 3:
                ok, _ = validate_ip_addr(content)
        if ok:
            color = GREEN
            self.pbApply.setEnabled(True)
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

    def switch_mode(self):
        # We purposefully discard changes other than hostname
        self._config.hostname = self.leHostname.text()
        config, self._config = self._config, None

        global NETWORK_MODE
        NETWORK_MODE = False

        display_config_window(config)

    def show(self, config: Configuration) -> None:
        self._config = config
        self.leHostname.setText(config.hostname)
        self.leMac.setText(config.mac.upper())
        self.leIP.setText(config.ip)
        self.leNetmask.setText(config.nm)
        self.leGateway.setText(config.gw)
        self.leBroadcast.setText(config.bc)
        self.cbReboot.setChecked(False)
        self.cbDynamic.setChecked(False)
        self.cbFlash.setChecked(False)
        self.parent.show()

    def query_dns(self):
        val = gethostbyname(self.leHostname.text())
        if val:
            self.leIP.setText(val)

    def reset(self):
        self.show(self._config)

    def apply(self):
        ips = [self.leNetmask.text(), self.leIP.text(),
               self.leGateway.text(), self.leBroadcast.text()]
        ok = self.validate_ip_range(*ips)
        if not ok:
            msg = 'One of the addresses is not within range of the others'
            QMessageBox.warning(self.parent, 'IPs not matching', msg)
            return

        msg = f'Reconfiguring {self._config.mac} ({self._config.hostname})'
        self.log.emit(msg)

        self.parent.close()
        config, self._config = self._config, None
        config.hostname = self.leHostname.text()
        config.ip = self.leIP.text()
        config.nw = self.leNetmask.text()
        config.gw = self.leGateway.text()
        config.bc = self.leBroadcast.text()
        config.reboot = self.cbReboot.isChecked()
        config.dynamic = self.cbDynamic.isChecked()
        config.flash = self.cbFlash.isChecked()

        ret = network.send_configuration(config)
        msg = f'{config.mac} ({config.hostname}) '
        if config.reboot:
            msg += 'will reboot. Please allow 45 seconds before it reappearing'
            QMessageBox.information(self.parent, 'Device Reboot', msg)
        elif ret is None:
            msg += 'did not send an acknowledgment in time!'
            QMessageBox.warning(self.parent, 'No acknowledgement!', msg)
        elif ret is acknowledgements.OK:
            msg += 'applied the config ok'
            QMessageBox.information(self.parent, 'Device reply', msg)
        else:
            msg += 'replied with {ret.name} [{ret.value}]'
            QMessageBox.warning(self.parent, 'Error on device!', msg)

        self.done.emit()

    @staticmethod
    def validate_ip_range(netmask, *ips):
        """Validate that all ips are within the netmask"""
        bytes_ = len([b for b in netmask.split('.') if b == '255'])
        ok = True
        for idx in range(len(ips)-1):
            current = ips[idx]
            current = '.'.join(current.split('.')[:bytes_])
            next_ = ips[idx+1]
            next_ = '.'.join(next_.split('.')[:bytes_])
            ok = ok and current == next_
        return ok
