# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Login_Window.ui'
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

class Ui_Login_Window(object):
    def setupUi(self, Login_Window):
        if not Login_Window.objectName():
            Login_Window.setObjectName(u"Login_Window")
        Login_Window.resize(441, 450)
        Login_Window.setStyleSheet(u"background-color: rgb(0, 0, 0);")
        self.centralwidget = QWidget(Login_Window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.Edit_ID = QLineEdit(self.centralwidget)
        self.Edit_ID.setObjectName(u"Edit_ID")
        self.Edit_ID.setGeometry(QRect(90, 80, 261, 51))
        self.Edit_ID.setStyleSheet(u"background-color: white;\n"
"")
        self.Edit_Password = QLineEdit(self.centralwidget)
        self.Edit_Password.setObjectName(u"Edit_Password")
        self.Edit_Password.setGeometry(QRect(90, 180, 261, 51))
        font = QFont()
        font.setPointSize(14)
        self.Edit_Password.setFont(font)
        self.Edit_Password.setStyleSheet(u"background-color: white;\n"
"")
        self.Edit_Password.setInputMethodHints(Qt.InputMethodHint.ImhHiddenText|Qt.InputMethodHint.ImhNoAutoUppercase|Qt.InputMethodHint.ImhNoPredictiveText|Qt.InputMethodHint.ImhSensitiveData)
        self.Edit_Password.setEchoMode(QLineEdit.EchoMode.Password)
        self.Text_ID = QLabel(self.centralwidget)
        self.Text_ID.setObjectName(u"Text_ID")
        self.Text_ID.setGeometry(QRect(90, 50, 81, 31))
        font1 = QFont()
        font1.setPointSize(16)
        self.Text_ID.setFont(font1)
        self.Text_ID.setStyleSheet(u"background: transparent;\n"
"color: rgb(255, 255, 255);")
        self.Text_Password = QLabel(self.centralwidget)
        self.Text_Password.setObjectName(u"Text_Password")
        self.Text_Password.setGeometry(QRect(90, 150, 101, 31))
        self.Text_Password.setFont(font1)
        self.Text_Password.setStyleSheet(u"background: transparent;\n"
"color: rgb(255, 255, 255);")
        self.login_Btn = QPushButton(self.centralwidget)
        self.login_Btn.setObjectName(u"login_Btn")
        self.login_Btn.setGeometry(QRect(130, 260, 181, 51))
        self.login_Btn.setFont(font1)
        self.login_Btn.setStyleSheet(u"background-color: rgb(0, 144, 255);\n"
"border-radius: 20px;")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(90, 320, 261, 20))
        self.label.setStyleSheet(u"background: transparent;\n"
"color: rgb(255, 255, 255);")
        self.Sinup_Btn = QPushButton(self.centralwidget)
        self.Sinup_Btn.setObjectName(u"Sinup_Btn")
        self.Sinup_Btn.setGeometry(QRect(130, 350, 181, 51))
        self.Sinup_Btn.setFont(font1)
        self.Sinup_Btn.setStyleSheet(u"background-color: rgb(176, 176, 176);\n"
"border-radius: 20px;")
        Login_Window.setCentralWidget(self.centralwidget)

        self.retranslateUi(Login_Window)

        QMetaObject.connectSlotsByName(Login_Window)
    # setupUi

    def retranslateUi(self, Login_Window):
        Login_Window.setWindowTitle(QCoreApplication.translate("Login_Window", u"MainWindow", None))
        self.Edit_ID.setText("")
        self.Edit_Password.setInputMask("")
        self.Edit_Password.setText("")
        self.Text_ID.setText(QCoreApplication.translate("Login_Window", u"\uc774 \ub984 :", None))
        self.Text_Password.setText(QCoreApplication.translate("Login_Window", u"\ud559 \ubc88 :", None))
        self.login_Btn.setText(QCoreApplication.translate("Login_Window", u"\ub85c\uadf8\uc778 \u2192", None))
        self.label.setText(QCoreApplication.translate("Login_Window", u"--------------------------------Or----------------------------------------------------------", None))
        self.Sinup_Btn.setText(QCoreApplication.translate("Login_Window", u"\ud68c\uc6d0\uac00\uc785", None))
    # retranslateUi

