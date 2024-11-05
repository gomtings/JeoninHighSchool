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

class Ui_Select_Day(object):
    def setupUi(self, Select_Day):
        if not Select_Day.objectName():
            Select_Day.setObjectName(u"Select_Day")
        Select_Day.resize(667, 409)
        self.centralwidget = QWidget(Select_Day)
        self.centralwidget.setObjectName(u"centralwidget")
        self.Day1 = QPushButton(self.centralwidget)
        self.Day1.setObjectName(u"Day1")
        self.Day1.setGeometry(QRect(90, 20, 221, 81))
        self.Day3 = QPushButton(self.centralwidget)
        self.Day3.setObjectName(u"Day3")
        self.Day3.setGeometry(QRect(90, 110, 221, 81))
        self.Day5 = QPushButton(self.centralwidget)
        self.Day5.setObjectName(u"Day5")
        self.Day5.setGeometry(QRect(90, 200, 221, 81))
        self.Day7 = QPushButton(self.centralwidget)
        self.Day7.setObjectName(u"Day7")
        self.Day7.setGeometry(QRect(90, 290, 221, 81))
        self.Day2 = QPushButton(self.centralwidget)
        self.Day2.setObjectName(u"Day2")
        self.Day2.setGeometry(QRect(320, 20, 221, 81))
        self.Day6 = QPushButton(self.centralwidget)
        self.Day6.setObjectName(u"Day6")
        self.Day6.setGeometry(QRect(320, 200, 221, 81))
        self.Day4 = QPushButton(self.centralwidget)
        self.Day4.setObjectName(u"Day4")
        self.Day4.setGeometry(QRect(320, 110, 221, 81))
        self.Day8 = QPushButton(self.centralwidget)
        self.Day8.setObjectName(u"Day8")
        self.Day8.setGeometry(QRect(320, 290, 221, 81))
        Select_Day.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(Select_Day)
        self.statusbar.setObjectName(u"statusbar")
        Select_Day.setStatusBar(self.statusbar)

        self.retranslateUi(Select_Day)

        QMetaObject.connectSlotsByName(Select_Day)
    # setupUi

    def retranslateUi(self, Select_Day):
        Select_Day.setWindowTitle(QCoreApplication.translate("Select_Day", u"MainWindow", None))
        self.Day1.setText(QCoreApplication.translate("Select_Day", u"Day1", None))
        self.Day3.setText(QCoreApplication.translate("Select_Day", u"Day3", None))
        self.Day5.setText(QCoreApplication.translate("Select_Day", u"Day5", None))
        self.Day7.setText(QCoreApplication.translate("Select_Day", u"Day7", None))
        self.Day2.setText(QCoreApplication.translate("Select_Day", u"Day2", None))
        self.Day6.setText(QCoreApplication.translate("Select_Day", u"Day6", None))
        self.Day4.setText(QCoreApplication.translate("Select_Day", u"Day4", None))
        self.Day8.setText(QCoreApplication.translate("Select_Day", u"Day8", None))
    # retranslateUi

