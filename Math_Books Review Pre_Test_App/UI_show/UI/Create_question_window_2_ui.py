# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Create_question_window_2.ui'
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
    QSizePolicy, QTextEdit, QWidget)

class Ui_Create_question_window(object):
    def setupUi(self, Create_question_window):
        if not Create_question_window.objectName():
            Create_question_window.setObjectName(u"Create_question_window")
        Create_question_window.resize(786, 680)
        self.centralwidget = QWidget(Create_question_window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.picture_view = QLabel(self.centralwidget)
        self.picture_view.setObjectName(u"picture_view")
        self.picture_view.setGeometry(QRect(10, 30, 611, 361))
        self.picture_view.setPixmap(QPixmap(u"../img/Basic_Photo.png"))
        self.picture_view.setScaledContents(True)
        self.find_picture = QPushButton(self.centralwidget)
        self.find_picture.setObjectName(u"find_picture")
        self.find_picture.setGeometry(QRect(630, 160, 151, 71))
        font = QFont()
        font.setPointSize(20)
        self.find_picture.setFont(font)
        self.submit_btn = QPushButton(self.centralwidget)
        self.submit_btn.setObjectName(u"submit_btn")
        self.submit_btn.setGeometry(QRect(630, 250, 151, 71))
        self.submit_btn.setFont(font)
        self.correc_answer_Edit = QTextEdit(self.centralwidget)
        self.correc_answer_Edit.setObjectName(u"correc_answer_Edit")
        self.correc_answer_Edit.setGeometry(QRect(10, 480, 611, 191))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 460, 131, 21))
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 3, 81, 21))
        font1 = QFont()
        font1.setPointSize(12)
        self.label_2.setFont(font1)
        self.Edit_Description = QTextEdit(self.centralwidget)
        self.Edit_Description.setObjectName(u"Edit_Description")
        self.Edit_Description.setGeometry(QRect(10, 400, 611, 51))
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
#if QT_CONFIG(tooltip)
        self.find_picture.setToolTip(QCoreApplication.translate("Create_question_window", u"<html><head/><body><p>\ubb38\uc81c\uc5d0 \ub123\uc744 \uc0ac\uc9c4\uc744 \uc120\ud0dd \ud569\ub2c8\ub2e4.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.find_picture.setText(QCoreApplication.translate("Create_question_window", u"\ucc3e\uae30", None))
#if QT_CONFIG(tooltip)
        self.submit_btn.setToolTip(QCoreApplication.translate("Create_question_window", u"<html><head/><body><p>\ubb38\uc81c\ub97c \uc81c\ucd9c \ud569\ub2c8\ub2e4.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.submit_btn.setText(QCoreApplication.translate("Create_question_window", u"\ucd9c\uc81c\ud558\uae30", None))
        self.label.setText(QCoreApplication.translate("Create_question_window", u"\uc815\ub2f5.", None))
        self.label_2.setText(QCoreApplication.translate("Create_question_window", u"\uc11c\uc220\ud615.", None))
    # retranslateUi

