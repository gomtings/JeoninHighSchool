# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QWidget)

class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        if not LoginWindow.objectName():
            LoginWindow.setObjectName(u"LoginWindow")
        LoginWindow.resize(425, 255)
        self.centralwidget = QWidget(LoginWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(150, 10, 121, 41))
        font = QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.name = QLineEdit(self.centralwidget)
        self.name.setObjectName(u"name")
        self.name.setGeometry(QRect(170, 70, 191, 41))
        self.name.setStyleSheet(u"QLineEdit {\n"
"    border: 1px solid black;\n"
"}\n"
"")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(60, 70, 101, 41))
        self.label_2.setFont(font)
        self.stunum = QLineEdit(self.centralwidget)
        self.stunum.setObjectName(u"stunum")
        self.stunum.setGeometry(QRect(170, 130, 191, 41))
        self.stunum.setStyleSheet(u"QLineEdit {\n"
"    border: 1px solid black;\n"
"}\n"
"")
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(60, 130, 101, 41))
        self.label_3.setFont(font)
        self.login = QPushButton(self.centralwidget)
        self.login.setObjectName(u"login")
        self.login.setGeometry(QRect(50, 200, 161, 51))
        font1 = QFont()
        font1.setPointSize(16)
        self.login.setFont(font1)
        self.insert_btn = QPushButton(self.centralwidget)
        self.insert_btn.setObjectName(u"insert_btn")
        self.insert_btn.setGeometry(QRect(210, 200, 161, 51))
        self.insert_btn.setFont(font1)
        LoginWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(LoginWindow)

        QMetaObject.connectSlotsByName(LoginWindow)
    # setupUi

    def retranslateUi(self, LoginWindow):
        LoginWindow.setWindowTitle(QCoreApplication.translate("LoginWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("LoginWindow", u"<\ub85c\uadf8\uc778>", None))
        self.name.setText("")
        self.label_2.setText(QCoreApplication.translate("LoginWindow", u"> \uc774\ub984 :", None))
        self.stunum.setText("")
        self.label_3.setText(QCoreApplication.translate("LoginWindow", u"> \ud559\ubc88 :", None))
        self.login.setText(QCoreApplication.translate("LoginWindow", u"\ub85c\uadf8\uc778", None))
        self.insert_btn.setText(QCoreApplication.translate("LoginWindow", u"\ud68c\uc6d0\uac00\uc785", None))
    # retranslateUi

