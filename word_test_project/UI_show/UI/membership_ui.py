# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'membership.ui'
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

class Ui_MembershipWindow(object):
    def setupUi(self, MembershipWindow):
        if not MembershipWindow.objectName():
            MembershipWindow.setObjectName(u"MembershipWindow")
        MembershipWindow.resize(425, 255)
        self.centralwidget = QWidget(MembershipWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(140, 10, 141, 41))
        font = QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.name = QLineEdit(self.centralwidget)
        self.name.setObjectName(u"name")
        self.name.setGeometry(QRect(180, 70, 161, 41))
        self.name.setStyleSheet(u"QLineEdit {\n"
"    border: 1px solid black;\n"
"}\n"
"")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(80, 70, 81, 41))
        self.label_2.setFont(font)
        self.stunum = QLineEdit(self.centralwidget)
        self.stunum.setObjectName(u"stunum")
        self.stunum.setGeometry(QRect(180, 130, 161, 41))
        self.stunum.setStyleSheet(u"QLineEdit {\n"
"    border: 1px solid black;\n"
"}\n"
"")
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(80, 130, 81, 41))
        self.label_3.setFont(font)
        self.insert_info = QPushButton(self.centralwidget)
        self.insert_info.setObjectName(u"insert_info")
        self.insert_info.setGeometry(QRect(80, 200, 261, 51))
        font1 = QFont()
        font1.setPointSize(16)
        self.insert_info.setFont(font1)
        MembershipWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MembershipWindow)

        QMetaObject.connectSlotsByName(MembershipWindow)
    # setupUi

    def retranslateUi(self, MembershipWindow):
        MembershipWindow.setWindowTitle(QCoreApplication.translate("MembershipWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MembershipWindow", u"<\ud68c\uc6d0\uac00\uc785>", None))
        self.name.setText("")
        self.label_2.setText(QCoreApplication.translate("MembershipWindow", u"> \uc774\ub984", None))
        self.stunum.setText("")
        self.label_3.setText(QCoreApplication.translate("MembershipWindow", u"> \ud559\ubc88", None))
        self.insert_info.setText(QCoreApplication.translate("MembershipWindow", u"\ud68c\uc6d0\uac00\uc785", None))
    # retranslateUi

