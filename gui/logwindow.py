from datetime import datetime as dt

from PyQt5.QtCore import pyqtSlot, QObject, QRect
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QFileDialog, QGroupBox,
                             QMessageBox, QTextEdit, QPushButton)


class LogWindow(QObject):
    """LogWindow displays a log of multicast messages, and actions within
    ipassing, with an option to save that to file.

    This window contains a read-only text field that, when displayed refreshes
    automatically.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        if parent is None:
            parent = QDialog()

        parent.setObjectName('logWindow')
        parent.setWindowTitle('IcePAP Logs')
        parent.resize(710, 480)
        self.parent = parent

        groupBox = QGroupBox(parent)
        groupBox.setObjectName('gbLog')
        groupBox.setGeometry(QRect(10, 10, 690, 400))
        groupBox.setTitle('Log')

        teLog = QTextEdit(groupBox)
        teLog.setObjectName('teLog')
        teLog.setGeometry(QRect(10, 20, 670, 370))
        teLog.setFont(QFont('monospace'))
        teLog.setReadOnly(True)
        self.teLog = teLog

        pbClose = QPushButton(parent)
        pbClose.setObjectName('pbClose')
        pbClose.setGeometry(QRect(20, 430, 120, 40))
        pbClose.setText('Close')
        pbClose.clicked.connect(parent.close)

        pbSave = QPushButton(parent)
        pbSave.setObjectName('pbSave')
        pbSave.setGeometry(QRect(570, 430, 120, 40))
        pbSave.setText('Save to File')
        pbSave.clicked.connect(self.save)

    def display(self):
        if not self.parent.isVisible():
            self.parent.show()

    @pyqtSlot(str)
    def log(self, content):
        header = dt.strftime(dt.now(), '%Y/%m/%d %H:%M:%S> ')
        self.teLog.append(header + content)

    def save(self):
        filename, _ = QFileDialog.getSaveFileName(
            self.parent, 'Select File', 'ipassign.log',
            'log files (*.log);;All files (*)')

        if filename:
            try:
                with open(filename, 'w') as fout:
                    fout.write(self.teLog.toPlainText())
                    fout.write('\n')
            except (OSError, PermissionError)as err:
                msg = f'Could not save log to {filename}!'
                if isinstance(err, PermissionError):
                    msg += '\nPermission Denied'
                QMessageBox.warning(self.parent, 'Could not save logs', msg)
