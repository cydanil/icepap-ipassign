import sys

from PyQt5.QtCore import pyqtSlot, QObject, QRect
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QPushButton

from .configurations import display_config_window
from .networking import network


class MainWindow(QObject):
    """MainWindow is the entry point of the ipassign application.

    This window contains a list of devices found on the network, of which the
    configuration can be modified in the HostnameSettings or NetworkSettings
    windows.
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        parent.setObjectName('mainWindow')
        parent.setWindowTitle('IcePAP remote configuration')
        parent.resize(620, 360)

        lwDevices = QListWidget(parent)
        lwDevices.setObjectName('devicesList')
        lwDevices.setGeometry(QRect(20, 30, 580, 170))
        lwDevices.setFont(QFont('monospace'))
        lwDevices.itemDoubleClicked.connect(self.open_properties)
        self.lwDevices = lwDevices

        pbQuit = QPushButton(parent)
        pbQuit.setObjectName('pbQuit')
        pbQuit.setGeometry(QRect(20, 300, 100, 40))
        pbQuit.setText('Quit')
        pbQuit.clicked.connect(sys.exit)

        pbLog = QPushButton(parent)
        pbLog.setObjectName('pbLog')
        pbLog.setGeometry(QRect(260, 300, 100, 40))
        pbLog.setText('View Log')
        self.pbLog = pbLog

        pbProperties = QPushButton(parent)
        pbProperties.setObjectName('pbProperties')
        pbProperties.setGeometry(QRect(500, 230, 100, 40))
        pbProperties.setText('Properties')
        pbProperties.setToolTip("The selected device's properties")
        pbProperties.clicked.connect(self.on_pbProperties_clicked)

        pbRefresh = QPushButton(parent)
        pbRefresh.setObjectName('pbRefresh')
        pbRefresh.setGeometry(QRect(500, 300, 100, 40))
        pbRefresh.setText('Refresh')
        pbRefresh.setToolTip("Scan devices on the network")
        pbRefresh.clicked.connect(self.list_devices)

        # self.devices is a dict of {mac address str: Configurations},
        # as set in self.list_devices()
        self.devices = None

    def list_devices(self):
        self.lwDevices.clear()
        devices = network.do_discovery()
        self.devices = {mac.upper(): config for mac, config in
                        sorted(devices.items(), key=lambda i: i[1].hostname)}

        for mac, device in self.devices.items():
            line = (mac + '    '
                    + f'{device.ip}'.ljust(16) + '    '
                    + device.hostname)
            self.lwDevices.addItem(line)

    @pyqtSlot(QListWidgetItem)
    def open_properties(self, item):
        if item is None:
            return
        mac = item.text().split()[0]
        config = self.devices[mac]
        display_config_window(config)

    def on_pbProperties_clicked(self):
        item = self.lwDevices.currentItem()
        if item is None:
            item = self.lwDevices.item(0)
        self.open_properties(item)
