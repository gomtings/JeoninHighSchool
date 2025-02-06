# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'grade_manager.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QLabel,
    QListWidget, QListWidgetItem, QSizePolicy, QWidget)

class Ui_grade_window(object):
    def setupUi(self, grade_window):
        if not grade_window.objectName():
            grade_window.setObjectName(u"grade_window")
        grade_window.resize(515, 543)
        self.grade_list = QListWidget(grade_window)
        self.grade_list.setObjectName(u"grade_list")
        self.grade_list.setGeometry(QRect(0, 80, 511, 461))
        font = QFont()
        font.setPointSize(16)
        self.grade_list.setFont(font)
        self.label = QLabel(grade_window)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 161, 71))
        font1 = QFont()
        font1.setPointSize(28)
        self.label.setFont(font1)
        self.Sorting = QComboBox(grade_window)
        self.Sorting.addItem("")
        self.Sorting.addItem("")
        self.Sorting.setObjectName(u"Sorting")
        self.Sorting.setGeometry(QRect(370, 30, 141, 41))
        self.label_2 = QLabel(grade_window)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(290, 40, 81, 21))
        font2 = QFont()
        font2.setPointSize(12)
        self.label_2.setFont(font2)
        self.label_3 = QLabel(grade_window)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(180, 40, 51, 21))
        self.label_3.setFont(font2)
        self.subject = QComboBox(grade_window)
        self.subject.addItem("")
        self.subject.addItem("")
        self.subject.addItem("")
        self.subject.addItem("")
        self.subject.addItem("")
        self.subject.addItem("")
        self.subject.addItem("")
        self.subject.addItem("")
        self.subject.addItem("")
        self.subject.setObjectName(u"subject")
        self.subject.setGeometry(QRect(230, 30, 61, 41))

        self.retranslateUi(grade_window)

        QMetaObject.connectSlotsByName(grade_window)
    # setupUi

    def retranslateUi(self, grade_window):
        grade_window.setWindowTitle(QCoreApplication.translate("grade_window", u"Dialog", None))
#if QT_CONFIG(tooltip)
        self.grade_list.setToolTip(QCoreApplication.translate("grade_window", u"<html><head/><body><p>\uc131\uc801\uc21c\uc73c\ub85c \uc815\ub82c \ub429\ub2c8\ub2e4. </p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("grade_window", u"<\uc131\uc801\ud45c>", None))
        self.Sorting.setItemText(0, QCoreApplication.translate("grade_window", u"\uc815\ub2f5\uc21c", None))
        self.Sorting.setItemText(1, QCoreApplication.translate("grade_window", u"\uc624\ub2f5\uc21c", None))

        self.label_2.setText(QCoreApplication.translate("grade_window", u"\uc815\ub82c\uae30\uc900 :", None))
        self.label_3.setText(QCoreApplication.translate("grade_window", u"\uacfc\ubaa9 :", None))
        self.subject.setItemText(0, QCoreApplication.translate("grade_window", u"ALL", None))
        self.subject.setItemText(1, QCoreApplication.translate("grade_window", u"DAY1", None))
        self.subject.setItemText(2, QCoreApplication.translate("grade_window", u"DAY2", None))
        self.subject.setItemText(3, QCoreApplication.translate("grade_window", u"DAY3", None))
        self.subject.setItemText(4, QCoreApplication.translate("grade_window", u"DAY4", None))
        self.subject.setItemText(5, QCoreApplication.translate("grade_window", u"DAY5", None))
        self.subject.setItemText(6, QCoreApplication.translate("grade_window", u"DAY6", None))
        self.subject.setItemText(7, QCoreApplication.translate("grade_window", u"DAY7", None))
        self.subject.setItemText(8, QCoreApplication.translate("grade_window", u"DAY8", None))

    # retranslateUi

