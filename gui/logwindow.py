from datetime import datetime as dt

from PyQt5.QtCore import QObject, QRect, Qt
from PyQt5.QtWidgets import (QCheckBox, QDialog, QFileDialog,
                             QGroupBox, QTextEdit, QPushButton)


class LogWindow(QObject):
    """LogWindow displays a log of multicast messages, and actions within
    ipassing, with an option to save that to file.

    This window contains a read-only text field that, when displayed refreshes
    automatically.
    The `append` checkbox allows to add to a file, instead of overwriting when
    saving
    """

    def __init__(self, parent=None):
        super(LogWindow, self).__init__(parent=parent)
        if parent is None:
            parent = QDialog()

        parent.setObjectName('logWindow')
        parent.setWindowTitle('ICEPAP Logs')
        parent.resize(710, 480)
        self.parent = parent

        groupBox = QGroupBox(parent)
        groupBox.setObjectName('gbLog')
        groupBox.setGeometry(QRect(10, 10, 690, 400))
        groupBox.setTitle('Log')

        teLog = QTextEdit(groupBox)
        teLog.setObjectName('teLog')
        teLog.setGeometry(QRect(10, 20, 670, 370))
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

        cbAppend = QCheckBox(parent)
        cbAppend.setObjectName('cbAppend')
        cbAppend.setGeometry(QRect(400, 430, 160, 40))
        cbAppend.setLayoutDirection(Qt.RightToLeft)
        cbAppend.setText('Append to File')
        self.cbAppend = cbAppend

    def display(self):
        if not self.parent.isVisible():
            self.parent.show()

    def log(self, content):
        header = dt.strftime(dt.now(), '%Y/%m/%d %H:%M:%S> ')
        self.teLog.append(header + content)

    def save(self):
        filename, _ = QFileDialog.getSaveFileName(
            self.parent, 'Select File', 'ipassign.log',
            'log files (*.log);;All files (*)')

        mode = 'a' if self.cbAppend.isChecked() else 'w'
        if filename:
            try:
                with open(filename, mode) as fout:
                    fout.write(self.teLog.toPlainText())
                    fout.write('\n')
                msg = f'Log saved to {filename}'
            except (OSError, PermissionError):
                msg = f'Could not save log to {filename}'
            self.log(msg)
