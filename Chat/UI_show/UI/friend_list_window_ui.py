# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'friend_list_window.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QPushButton,
    QScrollArea, QSizePolicy, QWidget)

class Ui_friend_list_window(object):
    def setupUi(self, friend_list_window):
        if not friend_list_window.objectName():
            friend_list_window.setObjectName(u"friend_list_window")
        friend_list_window.resize(325, 574)
        friend_list_window.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.centralwidget = QWidget(friend_list_window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.Scroll_Area = QScrollArea(self.centralwidget)
        self.Scroll_Area.setObjectName(u"Scroll_Area")
        self.Scroll_Area.setGeometry(QRect(0, 70, 321, 501))
        self.Scroll_Area.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 319, 499))
        self.Scroll_Area.setWidget(self.scrollAreaWidgetContents)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 181, 51))
        font = QFont()
        font.setPointSize(28)
        self.label.setFont(font)
        self.label.setStyleSheet(u"background: transparent;")
        self.setupBtn = QPushButton(self.centralwidget)
        self.setupBtn.setObjectName(u"setupBtn")
        self.setupBtn.setGeometry(QRect(210, 20, 111, 41))
        friend_list_window.setCentralWidget(self.centralwidget)

        self.retranslateUi(friend_list_window)

        QMetaObject.connectSlotsByName(friend_list_window)
    # setupUi

    def retranslateUi(self, friend_list_window):
        friend_list_window.setWindowTitle(QCoreApplication.translate("friend_list_window", u"MainWindow", None))
#if QT_CONFIG(tooltip)
        self.Scroll_Area.setToolTip(QCoreApplication.translate("friend_list_window", u"<html><head/><body><p>\uc7a5\ube44\uc758 \ud640 \uc9c1\uacbd \uc744 \uc124\uc815 \ud569\ub2c8\ub2e4. </p><p>\ud640 \uc9c1\uacbd\uc740 mm \ub2e8\uc704\ub85c \uc785\ub825 \ud558\uc5ec\uc57c \ud569\ub2c8\ub2e4.</p><p>\uc785\ub825 \uc608: 460</p><p>\uc785\ub825\uc774 \uc5c6\uc744 \uacbd\uc6b0 \uae30\ubcf8\uac12(\uc608\uc2dc\uc758 \uc9c1\uacbd)\uc73c\ub85c \uc9c0\uc815\ub429\ub2c8\ub2e4.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("friend_list_window", u"\uce5c\uad6c \ubaa9\ub85d", None))
        self.setupBtn.setText(QCoreApplication.translate("friend_list_window", u"\uc124 \uc815", None))
    # retranslateUi

