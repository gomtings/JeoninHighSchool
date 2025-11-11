# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Select_Type_Window.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QMainWindow,
    QPushButton, QSizePolicy, QWidget)

class Ui_Select_Type_Window(object):
    def setupUi(self, Select_Type_Window):
        if not Select_Type_Window.objectName():
            Select_Type_Window.setObjectName(u"Select_Type_Window")
        Select_Type_Window.resize(445, 176)
        self.centralwidget = QWidget(Select_Type_Window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.SelectTypeBox = QComboBox(self.centralwidget)
        self.SelectTypeBox.addItem("")
        self.SelectTypeBox.addItem("")
        self.SelectTypeBox.setObjectName(u"SelectTypeBox")
        self.SelectTypeBox.setGeometry(QRect(330, 50, 111, 41))
        font = QFont()
        font.setPointSize(18)
        self.SelectTypeBox.setFont(font)
        self.BookBox = QComboBox(self.centralwidget)
        self.BookBox.setObjectName(u"BookBox")
        self.BookBox.setGeometry(QRect(130, 50, 111, 41))
        font1 = QFont()
        font1.setPointSize(20)
        self.BookBox.setFont(font1)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(0, 50, 121, 41))
        self.label.setFont(font1)
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(250, 50, 81, 41))
        self.label_2.setFont(font1)
        self.title = QLabel(self.centralwidget)
        self.title.setObjectName(u"title")
        self.title.setGeometry(QRect(80, 10, 251, 31))
        self.title.setFont(font)
        self.SelectInfo = QLabel(self.centralwidget)
        self.SelectInfo.setObjectName(u"SelectInfo")
        self.SelectInfo.setGeometry(QRect(0, 150, 361, 21))
        font2 = QFont()
        font2.setPointSize(12)
        self.SelectInfo.setFont(font2)
        self.submitbtn = QPushButton(self.centralwidget)
        self.submitbtn.setObjectName(u"submitbtn")
        self.submitbtn.setGeometry(QRect(100, 100, 211, 41))
        font3 = QFont()
        font3.setPointSize(16)
        self.submitbtn.setFont(font3)
        Select_Type_Window.setCentralWidget(self.centralwidget)

        self.retranslateUi(Select_Type_Window)

        QMetaObject.connectSlotsByName(Select_Type_Window)
    # setupUi

    def retranslateUi(self, Select_Type_Window):
        Select_Type_Window.setWindowTitle(QCoreApplication.translate("Select_Type_Window", u"MainWindow", None))
        self.SelectTypeBox.setItemText(0, QCoreApplication.translate("Select_Type_Window", u"\uac1d\uad00\uc2dd", None))
        self.SelectTypeBox.setItemText(1, QCoreApplication.translate("Select_Type_Window", u"\uc8fc\uad00\uc2dd", None))

        self.label.setText(QCoreApplication.translate("Select_Type_Window", u"\ub3c4\uc11c\uc120\ud0dd :", None))
        self.label_2.setText(QCoreApplication.translate("Select_Type_Window", u"\uc720\ud615 :", None))
        self.title.setText(QCoreApplication.translate("Select_Type_Window", u"\ucd9c\uc81c \uc720\ud615 \ubc0f \ub3c4\uc11c \uc120\ud0dd", None))
        self.SelectInfo.setText(QCoreApplication.translate("Select_Type_Window", u"00 \uad8c \uc758 \ud604\uc7ac \uae4c\uc9c0 \ucd9c\uc81c\ub41c \ubb38\uc81c\ub294 00 \uac1c \uc785\ub2c8\ub2e4.", None))
        self.submitbtn.setText(QCoreApplication.translate("Select_Type_Window", u"\ucd9c\uc81c \ud558\uae30", None))
    # retranslateUi

