# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Chat_Window.ui'
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
from PySide6.QtWidgets import (QApplication, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QPushButton, QSizePolicy, QWidget)

class Ui_Chat_Window(object):
    def setupUi(self, Chat_Window):
        if not Chat_Window.objectName():
            Chat_Window.setObjectName(u"Chat_Window")
        Chat_Window.resize(375, 603)
        Chat_Window.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.centralwidget = QWidget(Chat_Window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.Message = QLineEdit(self.centralwidget)
        self.Message.setObjectName(u"Message")
        self.Message.setGeometry(QRect(0, 530, 281, 71))
        self.transmit = QPushButton(self.centralwidget)
        self.transmit.setObjectName(u"transmit")
        self.transmit.setGeometry(QRect(284, 540, 91, 51))
        self.ChatListWidget = QListWidget(self.centralwidget)
        self.ChatListWidget.setObjectName(u"ChatListWidget")
        self.ChatListWidget.setGeometry(QRect(0, 0, 371, 521))
        Chat_Window.setCentralWidget(self.centralwidget)

        self.retranslateUi(Chat_Window)

        QMetaObject.connectSlotsByName(Chat_Window)
    # setupUi

    def retranslateUi(self, Chat_Window):
        Chat_Window.setWindowTitle(QCoreApplication.translate("Chat_Window", u"MainWindow", None))
        self.transmit.setText(QCoreApplication.translate("Chat_Window", u"\uc804\uc1a1", None))
    # retranslateUi

