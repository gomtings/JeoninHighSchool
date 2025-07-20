# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Setting_Window.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QPushButton, QSizePolicy,
    QWidget)

class Ui_Setting_Window(object):
    def setupUi(self, Setting_Window):
        if not Setting_Window.objectName():
            Setting_Window.setObjectName(u"Setting_Window")
        Setting_Window.resize(276, 300)
        self.centralwidget = QWidget(Setting_Window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.Allow_search = QPushButton(self.centralwidget)
        self.Allow_search.setObjectName(u"Allow_search")
        self.Allow_search.setGeometry(QRect(10, 10, 251, 61))
        self.friendlist = QListWidget(self.centralwidget)
        self.friendlist.setObjectName(u"friendlist")
        self.friendlist.setGeometry(QRect(10, 110, 251, 131))
        self.friend_input = QLineEdit(self.centralwidget)
        self.friend_input.setObjectName(u"friend_input")
        self.friend_input.setGeometry(QRect(10, 250, 141, 31))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 80, 111, 21))
        font = QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.addlist = QPushButton(self.centralwidget)
        self.addlist.setObjectName(u"addlist")
        self.addlist.setGeometry(QRect(160, 250, 101, 31))
        font1 = QFont()
        font1.setPointSize(12)
        self.addlist.setFont(font1)
        Setting_Window.setCentralWidget(self.centralwidget)

        self.retranslateUi(Setting_Window)

        QMetaObject.connectSlotsByName(Setting_Window)
    # setupUi

    def retranslateUi(self, Setting_Window):
        Setting_Window.setWindowTitle(QCoreApplication.translate("Setting_Window", u"MainWindow", None))
        self.Allow_search.setText(QCoreApplication.translate("Setting_Window", u"\uce5c\uad6c \uac80\uc0c9 \ud5c8\uc6a9(\ud5c8\uc6a9)", None))
        self.label.setText(QCoreApplication.translate("Setting_Window", u"-\uce5c\uad6c \ubaa9\ub85d-", None))
        self.addlist.setText(QCoreApplication.translate("Setting_Window", u"\uce5c\uad6c \ucd94\uac00", None))
    # retranslateUi

