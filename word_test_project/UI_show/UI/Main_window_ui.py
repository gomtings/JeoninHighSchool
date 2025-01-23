# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
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

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(576, 396)
        self.questions = QPushButton(Form)
        self.questions.setObjectName(u"questions")
        self.questions.setGeometry(QRect(120, 10, 331, 71))
        font = QFont()
        font.setPointSize(20)
        self.questions.setFont(font)
        self.Recode = QPushButton(Form)
        self.Recode.setObjectName(u"Recode")
        self.Recode.setGeometry(QRect(120, 80, 331, 71))
        self.Recode.setFont(font)
        self.closed = QPushButton(Form)
        self.closed.setObjectName(u"closed")
        self.closed.setGeometry(QRect(120, 290, 331, 71))
        self.closed.setFont(font)
        self.Addition = QPushButton(Form)
        self.Addition.setObjectName(u"Addition")
        self.Addition.setGeometry(QRect(120, 150, 331, 71))
        self.Addition.setFont(font)
        self.note = QPushButton(Form)
        self.note.setObjectName(u"note")
        self.note.setGeometry(QRect(120, 220, 331, 71))
        self.note.setFont(font)
        self.login_btn = QPushButton(Form)
        self.login_btn.setObjectName(u"login_btn")
        self.login_btn.setGeometry(QRect(0, 90, 121, 61))
        self.login_btn.setFont(font)
        self.login_btn.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid black;\n"
"    background-color: rgba(255, 255, 255, 0); /* \ud22c\uba85\ud55c \ubc30\uacbd\uc0c9 */\n"
"}\n"
"")
        self.info = QLabel(Form)
        self.info.setObjectName(u"info")
        self.info.setGeometry(QRect(350, 370, 221, 21))
        font1 = QFont()
        font1.setPointSize(10)
        self.info.setFont(font1)
        self.info.setStyleSheet(u"QLabel { \n"
"    border: 1px solid rgba(0, 0, 0, 0); \n"
"}\n"
"")
        self.version = QLabel(Form)
        self.version.setObjectName(u"version")
        self.version.setGeometry(QRect(0, 370, 351, 21))
        self.version.setFont(font1)
        self.version.setStyleSheet(u"QLabel { \n"
"    border: 1px solid rgba(0, 0, 0, 0); \n"
"}\n"
"")
        self.Manager_btn = QPushButton(Form)
        self.Manager_btn.setObjectName(u"Manager_btn")
        self.Manager_btn.setGeometry(QRect(0, 160, 121, 61))
        self.Manager_btn.setFont(font)
        self.Manager_btn.setStyleSheet(u"QPushButton {\n"
"    border: none; /* Remove border */\n"
"    background-color: rgba(0, 0, 0, 0); /* Completely transparent background */\n"
"}\n"
"")

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.questions.setText(QCoreApplication.translate("Form", u"\ubb38\uc81c \ud480\uae30", None))
        self.Recode.setText(QCoreApplication.translate("Form", u"\uae30\ub85d", None))
        self.closed.setText(QCoreApplication.translate("Form", u"\uc885\ub8cc", None))
        self.Addition.setText(QCoreApplication.translate("Form", u"\uc2dc\ud5d8 \ubc94\uc704 \ucd94\uac00", None))
        self.note.setText(QCoreApplication.translate("Form", u"\ub2e8\uc5b4\uc7a5", None))
        self.login_btn.setText(QCoreApplication.translate("Form", u"\ub85c\uadf8\uc778", None))
        self.info.setText(QCoreApplication.translate("Form", u"\uc0ac\uc6a9\uc790 \ub2d8 \ub85c\uadf8\uc778 \ud6c4 \uc0ac\uc6a9\ud574 \uc8fc\uc138\uc694.", None))
        self.version.setText(QCoreApplication.translate("Form", u"SW \ubc84\uc804 : 25-01-22.01  |  \ud559\uc2b5\uc9c0 \ubc84\uc804 : 2025-01-10 10:55", None))
        self.Manager_btn.setText("")
    # retranslateUi

