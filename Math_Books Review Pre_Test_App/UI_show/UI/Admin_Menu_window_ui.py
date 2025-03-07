# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Admin_Menu_window.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QPushButton, QSizePolicy,
    QWidget)

class Ui_Admin_Menu_window(object):
    def setupUi(self, Admin_Menu_window):
        if not Admin_Menu_window.objectName():
            Admin_Menu_window.setObjectName(u"Admin_Menu_window")
        Admin_Menu_window.resize(573, 396)
        self.Manager_Setup = QPushButton(Admin_Menu_window)
        self.Manager_Setup.setObjectName(u"Manager_Setup")
        self.Manager_Setup.setGeometry(QRect(120, 10, 331, 71))
        font = QFont()
        font.setPointSize(20)
        self.Manager_Setup.setFont(font)
        self.Account_Remove = QPushButton(Admin_Menu_window)
        self.Account_Remove.setObjectName(u"Account_Remove")
        self.Account_Remove.setGeometry(QRect(120, 80, 331, 71))
        self.Account_Remove.setFont(font)
        self.closed = QPushButton(Admin_Menu_window)
        self.closed.setObjectName(u"closed")
        self.closed.setGeometry(QRect(120, 290, 331, 71))
        self.closed.setFont(font)
        self.Addition = QPushButton(Admin_Menu_window)
        self.Addition.setObjectName(u"Addition")
        self.Addition.setGeometry(QRect(120, 220, 331, 71))
        self.Addition.setFont(font)
        self.Grade_Manager = QPushButton(Admin_Menu_window)
        self.Grade_Manager.setObjectName(u"Grade_Manager")
        self.Grade_Manager.setGeometry(QRect(120, 150, 331, 71))
        self.Grade_Manager.setFont(font)
        self.info = QLabel(Admin_Menu_window)
        self.info.setObjectName(u"info")
        self.info.setGeometry(QRect(350, 370, 221, 21))
        font1 = QFont()
        font1.setPointSize(10)
        self.info.setFont(font1)
        self.info.setStyleSheet(u"QLabel { \n"
"    border: 1px solid rgba(0, 0, 0, 0); \n"
"}\n"
"")
        self.version = QLabel(Admin_Menu_window)
        self.version.setObjectName(u"version")
        self.version.setGeometry(QRect(0, 370, 351, 21))
        self.version.setFont(font1)
        self.version.setStyleSheet(u"QLabel { \n"
"    border: 1px solid rgba(0, 0, 0, 0); \n"
"}\n"
"")

        self.retranslateUi(Admin_Menu_window)

        QMetaObject.connectSlotsByName(Admin_Menu_window)
    # setupUi

    def retranslateUi(self, Admin_Menu_window):
        Admin_Menu_window.setWindowTitle(QCoreApplication.translate("Admin_Menu_window", u"Form", None))
        self.Manager_Setup.setText(QCoreApplication.translate("Admin_Menu_window", u"\uad00\ub9ac\uc790 \uad8c\ud55c \uad00\ub9ac", None))
        self.Account_Remove.setText(QCoreApplication.translate("Admin_Menu_window", u"\uacc4\uc815 \uc0ad\uc81c", None))
        self.closed.setText(QCoreApplication.translate("Admin_Menu_window", u"\uc885\ub8cc", None))
        self.Addition.setText(QCoreApplication.translate("Admin_Menu_window", u"\uc2dc\ud5d8 \ubc94\uc704 \ucd94\uac00", None))
        self.Grade_Manager.setText(QCoreApplication.translate("Admin_Menu_window", u"\uc131\uc801 \uad00\ub9ac", None))
        self.info.setText(QCoreApplication.translate("Admin_Menu_window", u"\uc0ac\uc6a9\uc790 \ub2d8 \ub85c\uadf8\uc778 \ud6c4 \uc0ac\uc6a9\ud574 \uc8fc\uc138\uc694.", None))
        self.version.setText(QCoreApplication.translate("Admin_Menu_window", u"SW \ubc84\uc804 : 25-01-22.01  |  \ud559\uc2b5\uc9c0 \ubc84\uc804 : 2025-01-10 10:55", None))
    # retranslateUi

