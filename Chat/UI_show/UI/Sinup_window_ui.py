# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Sinup_window.ui'
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

class Ui_Sinup_window(object):
    def setupUi(self, Sinup_window):
        if not Sinup_window.objectName():
            Sinup_window.setObjectName(u"Sinup_window")
        Sinup_window.resize(425, 342)
        Sinup_window.setStyleSheet(u"background-color: rgb(0, 0, 0);")
        self.centralwidget = QWidget(Sinup_window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(140, 10, 141, 41))
        font = QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setStyleSheet(u"background: transparent;\n"
"color: rgb(255, 255, 255);")
        self.sinup = QPushButton(self.centralwidget)
        self.sinup.setObjectName(u"sinup")
        self.sinup.setGeometry(QRect(70, 270, 281, 51))
        font1 = QFont()
        font1.setPointSize(16)
        self.sinup.setFont(font1)
        self.sinup.setStyleSheet(u"background-color: rgb(0, 144, 255);\n"
"border-radius: 20px;")
        self.Text_ID = QLabel(self.centralwidget)
        self.Text_ID.setObjectName(u"Text_ID")
        self.Text_ID.setGeometry(QRect(80, 70, 81, 31))
        self.Text_ID.setFont(font1)
        self.Text_ID.setStyleSheet(u"background: transparent;\n"
"color: rgb(255, 255, 255);")
        self.Text_Password = QLabel(self.centralwidget)
        self.Text_Password.setObjectName(u"Text_Password")
        self.Text_Password.setGeometry(QRect(80, 160, 101, 31))
        self.Text_Password.setFont(font1)
        self.Text_Password.setStyleSheet(u"background: transparent;\n"
"color: rgb(255, 255, 255);")
        self.Edit_ID = QLineEdit(self.centralwidget)
        self.Edit_ID.setObjectName(u"Edit_ID")
        self.Edit_ID.setGeometry(QRect(80, 100, 261, 51))
        self.Edit_ID.setStyleSheet(u"background-color: white;\n"
"")
        self.Edit_Password = QLineEdit(self.centralwidget)
        self.Edit_Password.setObjectName(u"Edit_Password")
        self.Edit_Password.setGeometry(QRect(80, 190, 261, 51))
        font2 = QFont()
        font2.setPointSize(14)
        self.Edit_Password.setFont(font2)
        self.Edit_Password.setStyleSheet(u"background-color: white;\n"
"")
        self.Edit_Password.setInputMethodHints(Qt.InputMethodHint.ImhHiddenText|Qt.InputMethodHint.ImhNoAutoUppercase|Qt.InputMethodHint.ImhNoPredictiveText|Qt.InputMethodHint.ImhSensitiveData)
        self.Edit_Password.setEchoMode(QLineEdit.EchoMode.Password)
        Sinup_window.setCentralWidget(self.centralwidget)

        self.retranslateUi(Sinup_window)

        QMetaObject.connectSlotsByName(Sinup_window)
    # setupUi

    def retranslateUi(self, Sinup_window):
        Sinup_window.setWindowTitle(QCoreApplication.translate("Sinup_window", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("Sinup_window", u"<\ud68c\uc6d0\uac00\uc785>", None))
        self.sinup.setText(QCoreApplication.translate("Sinup_window", u"\ud68c\uc6d0\uac00\uc785", None))
        self.Text_ID.setText(QCoreApplication.translate("Sinup_window", u"\uc774 \ub984 :", None))
        self.Text_Password.setText(QCoreApplication.translate("Sinup_window", u"\ud559 \ubc88 :", None))
        self.Edit_ID.setText("")
        self.Edit_Password.setInputMask("")
        self.Edit_Password.setText("")
    # retranslateUi

