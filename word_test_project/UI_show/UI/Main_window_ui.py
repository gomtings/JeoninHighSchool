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
        Form.resize(533, 369)
        self.questions = QPushButton(Form)
        self.questions.setObjectName(u"questions")
        self.questions.setGeometry(QRect(120, 10, 281, 71))
        self.Recode = QPushButton(Form)
        self.Recode.setObjectName(u"Recode")
        self.Recode.setGeometry(QRect(120, 80, 281, 71))
        self.closed = QPushButton(Form)
        self.closed.setObjectName(u"closed")
        self.closed.setGeometry(QRect(120, 290, 281, 71))
        self.Addition = QPushButton(Form)
        self.Addition.setObjectName(u"Addition")
        self.Addition.setGeometry(QRect(120, 150, 281, 71))
        self.note = QPushButton(Form)
        self.note.setObjectName(u"note")
        self.note.setGeometry(QRect(120, 220, 281, 71))
        self.login_btn = QPushButton(Form)
        self.login_btn.setObjectName(u"login_btn")
        self.login_btn.setGeometry(QRect(0, 60, 121, 51))
        self.login_btn.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid black;\n"
"    background-color: rgba(255, 255, 255, 0); /* \ud22c\uba85\ud55c \ubc30\uacbd\uc0c9 */\n"
"}\n"
"")
        self.info = QLabel(Form)
        self.info.setObjectName(u"info")
        self.info.setGeometry(QRect(411, 343, 121, 21))
        self.info.setStyleSheet(u"QLabel { border: 1px solid black; }")

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
        self.info.setText(QCoreApplication.translate("Form", u"ABCDEFGFIJKLMN", None))
    # retranslateUi

