# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Manager.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QPushButton, QSizePolicy, QWidget)

class Ui_Manager_window(object):
    def setupUi(self, Manager_window):
        if not Manager_window.objectName():
            Manager_window.setObjectName(u"Manager_window")
        Manager_window.resize(376, 365)
        self.assignment = QPushButton(Manager_window)
        self.assignment.setObjectName(u"assignment")
        self.assignment.setGeometry(QRect(20, 10, 331, 71))
        font = QFont()
        font.setPointSize(20)
        self.assignment.setFont(font)
        self.Account_remove = QPushButton(Manager_window)
        self.Account_remove.setObjectName(u"Account_remove")
        self.Account_remove.setGeometry(QRect(20, 80, 331, 71))
        self.Account_remove.setFont(font)
        self.closed = QPushButton(Manager_window)
        self.closed.setObjectName(u"closed")
        self.closed.setGeometry(QRect(20, 290, 331, 71))
        self.closed.setFont(font)
        self.Addition = QPushButton(Manager_window)
        self.Addition.setObjectName(u"Addition")
        self.Addition.setGeometry(QRect(20, 150, 331, 71))
        self.Addition.setFont(font)
        self.note = QPushButton(Manager_window)
        self.note.setObjectName(u"note")
        self.note.setGeometry(QRect(20, 220, 331, 71))
        self.note.setFont(font)

        self.retranslateUi(Manager_window)

        QMetaObject.connectSlotsByName(Manager_window)
    # setupUi

    def retranslateUi(self, Manager_window):
        Manager_window.setWindowTitle(QCoreApplication.translate("Manager_window", u"Form", None))
        self.assignment.setText(QCoreApplication.translate("Manager_window", u"\uad00\ub9ac\uc790 \uad8c\ud55c \ubd80\uc5ec", None))
        self.Account_remove.setText(QCoreApplication.translate("Manager_window", u"\uacc4\uc815 \uc0ad\uc81c", None))
        self.closed.setText(QCoreApplication.translate("Manager_window", u"-", None))
        self.Addition.setText(QCoreApplication.translate("Manager_window", u"-", None))
        self.note.setText(QCoreApplication.translate("Manager_window", u"-", None))
    # retranslateUi

