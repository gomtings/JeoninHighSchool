# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'project_main.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QSizePolicy,
    QStatusBar, QWidget)
import sys
class Ui_Word_list(object):
    def setupUi(self, Word_list):
        if not Word_list.objectName():
            Word_list.setObjectName(u"Word_list")
        Word_list.resize(233, 286)
        self.centralwidget = QWidget(Word_list)
        self.centralwidget.setObjectName(u"centralwidget")
        self.btn_1 = QPushButton(self.centralwidget)
        self.btn_1.setObjectName(u"btn_1")
        self.btn_1.setGeometry(QRect(200, 10, 221, 81))
        self.btn_2 = QPushButton(self.centralwidget)
        self.btn_2.setObjectName(u"btn_2")
        self.btn_2.setGeometry(QRect(200, 100, 221, 81))
        self.btn_3 = QPushButton(self.centralwidget)
        self.btn_3.setObjectName(u"btn_3")
        self.btn_3.setGeometry(QRect(200, 190, 221, 81))
        self.btn_4 = QPushButton(self.centralwidget)
        self.btn_4.setObjectName(u"btn_4")
        self.btn_4.setGeometry(QRect(200, 280, 221, 81))
        self.btn_5 = QPushButton(self.centralwidget)
        self.btn_5.setObjectName(u"btn_5")
        self.btn_5.setGeometry(QRect(430, 10, 221, 81))
        self.btn_6 = QPushButton(self.centralwidget)
        self.btn_6.setObjectName(u"btn_6")
        self.btn_6.setGeometry(QRect(430, 190, 221, 81))
        self.btn_7 = QPushButton(self.centralwidget)
        self.btn_7.setObjectName(u"btn_7")
        self.btn_7.setGeometry(QRect(430, 100, 221, 81))
        self.btn_8 = QPushButton(self.centralwidget)
        self.btn_8.setObjectName(u"btn_8")
        self.btn_8.setGeometry(QRect(430, 280, 221, 81))
        Word_list.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(Word_list)
        self.statusbar.setObjectName(u"statusbar")
        Word_list.setStatusBar(self.statusbar)

        self.retranslateUi(Word_list)

        QMetaObject.connectSlotsByName(Word_list)
    # setupUi

    def retranslateUi(self, Word_list):
        Word_list.setWindowTitle(QCoreApplication.translate("Word_list", u"MainWindow", None))
        self.btn_1.setText(QCoreApplication.translate("Word_list", u"Day1", None))
        self.btn_2.setText(QCoreApplication.translate("Word_list", u"Day3", None))
        self.btn_3.setText(QCoreApplication.translate("Word_list", u"Day5", None))
        self.btn_4.setText(QCoreApplication.translate("Word_list", u"Day7", None))
        self.btn_5.setText(QCoreApplication.translate("Word_list", u"Day2", None))
        self.btn_6.setText(QCoreApplication.translate("Word_list", u"Day6", None))
        self.btn_7.setText(QCoreApplication.translate("Word_list", u"Day4", None))
        self.btn_8.setText(QCoreApplication.translate("Word_list", u"Day8", None))
    # retranslateUi