# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Create_question_window.ui'
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
    QPushButton, QRadioButton, QSizePolicy, QWidget)

class Ui_Create_question_window(object):
    def setupUi(self, Create_question_window):
        if not Create_question_window.objectName():
            Create_question_window.setObjectName(u"Create_question_window")
        Create_question_window.resize(786, 633)
        self.centralwidget = QWidget(Create_question_window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.picture_view = QLabel(self.centralwidget)
        self.picture_view.setObjectName(u"picture_view")
        self.picture_view.setGeometry(QRect(10, 20, 611, 361))
        self.picture_view.setPixmap(QPixmap(u"../img/Basic_Photo.png"))
        self.picture_view.setScaledContents(True)
        self.find_picture = QPushButton(self.centralwidget)
        self.find_picture.setObjectName(u"find_picture")
        self.find_picture.setGeometry(QRect(630, 160, 151, 71))
        font = QFont()
        font.setPointSize(20)
        self.find_picture.setFont(font)
        self.Edit_Description = QLineEdit(self.centralwidget)
        self.Edit_Description.setObjectName(u"Edit_Description")
        self.Edit_Description.setGeometry(QRect(10, 390, 611, 41))
        self.answer_1 = QRadioButton(self.centralwidget)
        self.answer_1.setObjectName(u"answer_1")
        self.answer_1.setGeometry(QRect(60, 440, 561, 31))
        font1 = QFont()
        font1.setPointSize(12)
        self.answer_1.setFont(font1)
        self.answer_1.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.answer_2 = QRadioButton(self.centralwidget)
        self.answer_2.setObjectName(u"answer_2")
        self.answer_2.setGeometry(QRect(60, 480, 561, 31))
        self.answer_2.setFont(font1)
        self.answer_3 = QRadioButton(self.centralwidget)
        self.answer_3.setObjectName(u"answer_3")
        self.answer_3.setGeometry(QRect(60, 520, 561, 31))
        self.answer_3.setFont(font1)
        self.answer_5 = QRadioButton(self.centralwidget)
        self.answer_5.setObjectName(u"answer_5")
        self.answer_5.setGeometry(QRect(60, 600, 561, 31))
        self.answer_5.setFont(font1)
        self.answer_4 = QRadioButton(self.centralwidget)
        self.answer_4.setObjectName(u"answer_4")
        self.answer_4.setGeometry(QRect(60, 560, 561, 31))
        self.answer_4.setFont(font1)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 440, 31, 31))
        font2 = QFont()
        font2.setPointSize(14)
        self.label.setFont(font2)
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 480, 31, 31))
        self.label_2.setFont(font2)
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 520, 31, 31))
        self.label_3.setFont(font2)
        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(20, 560, 31, 31))
        self.label_4.setFont(font2)
        self.label_5 = QLabel(self.centralwidget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(20, 600, 31, 31))
        self.label_5.setFont(font2)
        self.submit_btn = QPushButton(self.centralwidget)
        self.submit_btn.setObjectName(u"submit_btn")
        self.submit_btn.setGeometry(QRect(630, 250, 151, 71))
        self.submit_btn.setFont(font)
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
        self.Edit_Description.setToolTip(QCoreApplication.translate("Create_question_window", u"<html><head/><body><p>\ubb38\uc81c \uc5d0 \ub300\ud55c \uc124\uba85\uc744 \uc785\ub825\ud574 \uc8fc\uc138\uc694.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.answer_1.setText(QCoreApplication.translate("Create_question_window", u"\uc815\ub2f5 1", None))
        self.answer_2.setText(QCoreApplication.translate("Create_question_window", u"\uc815\ub2f5 2", None))
        self.answer_3.setText(QCoreApplication.translate("Create_question_window", u"\uc815\ub2f5 3", None))
        self.answer_5.setText(QCoreApplication.translate("Create_question_window", u"\uc815\ub2f5 5", None))
        self.answer_4.setText(QCoreApplication.translate("Create_question_window", u"\uc815\ub2f5 4", None))
        self.label.setText(QCoreApplication.translate("Create_question_window", u"1.", None))
        self.label_2.setText(QCoreApplication.translate("Create_question_window", u"2.", None))
        self.label_3.setText(QCoreApplication.translate("Create_question_window", u"3.", None))
        self.label_4.setText(QCoreApplication.translate("Create_question_window", u"4.", None))
        self.label_5.setText(QCoreApplication.translate("Create_question_window", u"4.", None))
#if QT_CONFIG(tooltip)
        self.submit_btn.setToolTip(QCoreApplication.translate("Create_question_window", u"<html><head/><body><p>\ubb38\uc81c\ub97c \uc81c\ucd9c \ud569\ub2c8\ub2e4.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.submit_btn.setText(QCoreApplication.translate("Create_question_window", u"\ucd9c\uc81c\ud558\uae30", None))
    # retranslateUi

