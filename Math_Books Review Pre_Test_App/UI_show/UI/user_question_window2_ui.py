# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'user_question_window2.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
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
    QSizePolicy, QTextEdit, QWidget)

class Ui_Create_question_window(object):
    def setupUi(self, Create_question_window):
        if not Create_question_window.objectName():
            Create_question_window.setObjectName(u"Create_question_window")
        Create_question_window.resize(771, 680)
        self.centralwidget = QWidget(Create_question_window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.picture_view = QLabel(self.centralwidget)
        self.picture_view.setObjectName(u"picture_view")
        self.picture_view.setGeometry(QRect(10, 30, 611, 361))
        self.picture_view.setPixmap(QPixmap(u"../img/Basic_Photo.png"))
        self.picture_view.setScaledContents(True)
        self.correc_answer_Edit = QTextEdit(self.centralwidget)
        self.correc_answer_Edit.setObjectName(u"correc_answer_Edit")
        self.correc_answer_Edit.setGeometry(QRect(10, 470, 611, 201))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 450, 131, 21))
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 3, 81, 21))
        font = QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.input_Description = QLabel(self.centralwidget)
        self.input_Description.setObjectName(u"input_Description")
        self.input_Description.setGeometry(QRect(17, 410, 601, 21))
        self.input_Description.setFont(font)
        self.submitbtn = QPushButton(self.centralwidget)
        self.submitbtn.setObjectName(u"submitbtn")
        self.submitbtn.setGeometry(QRect(630, 320, 131, 71))
        font1 = QFont()
        font1.setPointSize(22)
        self.submitbtn.setFont(font1)
        Create_question_window.setCentralWidget(self.centralwidget)

        self.retranslateUi(Create_question_window)

        QMetaObject.connectSlotsByName(Create_question_window)
    # setupUi

    def retranslateUi(self, Create_question_window):
        Create_question_window.setWindowTitle(QCoreApplication.translate("Create_question_window", u"MainWindow", None))
#if QT_CONFIG(tooltip)
        self.picture_view.setToolTip(QCoreApplication.translate("Create_question_window", u"<html><head/><body><p>\ubb38\uc81c\uc5d0 \ub300\ud55c \uc774\ubbf8\uc9c0\ub97c \ub123\uc5b4 \uc8fc\uc138\uc694.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.picture_view.setText("")
        self.label.setText(QCoreApplication.translate("Create_question_window", u"\uc815\ub2f5.", None))
        self.label_2.setText(QCoreApplication.translate("Create_question_window", u"\uc11c\uc220\ud615.", None))
        self.input_Description.setText(QCoreApplication.translate("Create_question_window", u"\ubb38\uc81c :", None))
        self.submitbtn.setText(QCoreApplication.translate("Create_question_window", u"\uc81c\ucd9c\ud558\uae30", None))
    # retranslateUi

