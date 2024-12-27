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
        self.record_list = QListWidget(record)
        self.record_list.setObjectName(u"record_list")
        self.record_list.setGeometry(QRect(20, 80, 821, 511))
        font = QFont()
        font.setPointSize(20)
        self.record_list.setFont(font)
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
        self.label.setText(QCoreApplication.translate("record", u"\uae30\ub85d", None))
    # retranslateUi

