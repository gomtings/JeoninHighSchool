# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'record.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QListWidget,
    QListWidgetItem, QSizePolicy, QWidget)

class Ui_record(object):
    def setupUi(self, record):
        if not record.objectName():
            record.setObjectName(u"record")
        record.resize(864, 633)
        self.listWidget_2 = QListWidget(record)
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        QListWidgetItem(self.listWidget_2)
        self.listWidget_2.setObjectName(u"listWidget_2")
        self.listWidget_2.setGeometry(QRect(20, 80, 821, 511))
        font = QFont()
        font.setPointSize(20)
        self.listWidget_2.setFont(font)
        self.label = QLabel(record)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(390, 10, 81, 71))
        font1 = QFont()
        font1.setPointSize(28)
        self.label.setFont(font1)

        self.retranslateUi(record)

        QMetaObject.connectSlotsByName(record)
    # setupUi

    def retranslateUi(self, record):
        record.setWindowTitle(QCoreApplication.translate("record", u"Dialog", None))

        __sortingEnabled = self.listWidget_2.isSortingEnabled()
        self.listWidget_2.setSortingEnabled(False)
        ___qlistwidgetitem = self.listWidget_2.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("record", u"2024/11/12 PM 9:55 Day1", None));
        ___qlistwidgetitem1 = self.listWidget_2.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("record", u"2024/11/12 PM 9:55 Day2", None));
        ___qlistwidgetitem2 = self.listWidget_2.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("record", u"2024/11/12 PM 9:55 Day3", None));
        ___qlistwidgetitem3 = self.listWidget_2.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("record", u"2024/11/12 PM 9:55 Day5", None));
        ___qlistwidgetitem4 = self.listWidget_2.item(4)
        ___qlistwidgetitem4.setText(QCoreApplication.translate("record", u"2024/11/12 PM 9:55 Day4", None));
        ___qlistwidgetitem5 = self.listWidget_2.item(5)
        ___qlistwidgetitem5.setText(QCoreApplication.translate("record", u"2024/11/12 PM 9:55 Day6", None));
        self.listWidget_2.setSortingEnabled(__sortingEnabled)

        self.label.setText(QCoreApplication.translate("record", u"\uae30\ub85d", None))
    # retranslateUi

