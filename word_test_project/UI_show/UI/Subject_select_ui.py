# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Subject_select.ui'
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

class Ui_Subject(object):
    def setupUi(self, Subject):
        if not Subject.objectName():
            Subject.setObjectName(u"Subject")
        Subject.resize(372, 136)
        self.centralwidget = QWidget(Subject)
        self.centralwidget.setObjectName(u"centralwidget")
        self.title = QLabel(self.centralwidget)
        self.title.setObjectName(u"title")
        self.title.setGeometry(QRect(120, 10, 121, 41))
        font = QFont()
        font.setPointSize(20)
        self.title.setFont(font)
        self.Subject_select = QComboBox(self.centralwidget)
        self.Subject_select.addItem("")
        self.Subject_select.addItem("")
        self.Subject_select.addItem("")
        self.Subject_select.addItem("")
        self.Subject_select.addItem("")
        self.Subject_select.addItem("")
        self.Subject_select.addItem("")
        self.Subject_select.addItem("")
        self.Subject_select.addItem("")
        self.Subject_select.setObjectName(u"Subject_select")
        self.Subject_select.setGeometry(QRect(30, 50, 311, 41))
        font1 = QFont()
        font1.setPointSize(16)
        self.Subject_select.setFont(font1)
        self.start_exam = QPushButton(self.centralwidget)
        self.start_exam.setObjectName(u"start_exam")
        self.start_exam.setGeometry(QRect(100, 90, 171, 51))
        font2 = QFont()
        font2.setPointSize(14)
        self.start_exam.setFont(font2)
        Subject.setCentralWidget(self.centralwidget)

        self.retranslateUi(Subject)

        QMetaObject.connectSlotsByName(Subject)
    # setupUi

    def retranslateUi(self, Subject):
        Subject.setWindowTitle(QCoreApplication.translate("Subject", u"MainWindow", None))
        self.title.setText(QCoreApplication.translate("Subject", u"\uacfc\ubaa9 \uc120\ud0dd", None))
        self.Subject_select.setItemText(0, QCoreApplication.translate("Subject", u"DAY1", None))
        self.Subject_select.setItemText(1, QCoreApplication.translate("Subject", u"DAY2", None))
        self.Subject_select.setItemText(2, QCoreApplication.translate("Subject", u"DAY3", None))
        self.Subject_select.setItemText(3, QCoreApplication.translate("Subject", u"DAY4", None))
        self.Subject_select.setItemText(4, QCoreApplication.translate("Subject", u"DAY5", None))
        self.Subject_select.setItemText(5, QCoreApplication.translate("Subject", u"DAY6", None))
        self.Subject_select.setItemText(6, QCoreApplication.translate("Subject", u"DAY7", None))
        self.Subject_select.setItemText(7, QCoreApplication.translate("Subject", u"DAY8", None))
        self.Subject_select.setItemText(8, QCoreApplication.translate("Subject", u"DAY9", None))

        self.start_exam.setText(QCoreApplication.translate("Subject", u"DAY1 \uc2dc\ud5d8 \ubcf4\uae30", None))
    # retranslateUi

