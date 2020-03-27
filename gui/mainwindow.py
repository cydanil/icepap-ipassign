import sys

from PyQt5.QtCore import QObject, QRect
from PyQt5.QtWidgets import QListWidget, QPushButton


class MainWindow(QObject):
    """MainWindow is the entry point of the ipassign application.

    This window contains a list of devices found on the network, of which the
    configuration can be modified in the HostnameSettings or NetworkSettings
    windows.
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        parent.setObjectName('mainWindow')
        parent.setWindowTitle('ICEPAP remote configuration')
        parent.resize(620, 360)

        devicesList = QListWidget(parent)
        devicesList.setObjectName('devicesList')
        devicesList.setGeometry(QRect(20, 30, 580, 170))
        devicesList.addItem('No data yet')
        self.devicesList = devicesList

        pbQuit = QPushButton(parent)
        pbQuit.setObjectName('pbQuit')
        pbQuit.setGeometry(QRect(20, 300, 100, 40))
        pbQuit.setText('Quit')
        pbQuit.clicked.connect(sys.exit)
        self.pbQuit = pbQuit

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
        self.pbProperties = pbProperties

        pbRefresh = QPushButton(parent)
        pbRefresh.setObjectName('pbRefresh')
        pbRefresh.setGeometry(QRect(500, 300, 100, 40))
        pbRefresh.setText('Refresh')
        pbRefresh.setToolTip("Scan devices on the network")
        self.pbRefresh = pbRefresh
