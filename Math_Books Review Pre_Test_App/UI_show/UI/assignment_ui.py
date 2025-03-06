# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'assignment.ui'
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

class Ui_assignment_window(object):
    def setupUi(self, assignment_window):
        if not assignment_window.objectName():
            assignment_window.setObjectName(u"assignment_window")
        assignment_window.resize(391, 473)
        self.Account_list = QListWidget(assignment_window)
        self.Account_list.setObjectName(u"Account_list")
        self.Account_list.setGeometry(QRect(20, 80, 351, 391))
        font = QFont()
        font.setPointSize(20)
        self.Account_list.setFont(font)
        self.label = QLabel(assignment_window)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(110, 10, 171, 71))
        font1 = QFont()
        font1.setPointSize(28)
        self.label.setFont(font1)

        self.retranslateUi(assignment_window)

        QMetaObject.connectSlotsByName(assignment_window)
    # setupUi

    def retranslateUi(self, assignment_window):
        assignment_window.setWindowTitle(QCoreApplication.translate("assignment_window", u"Dialog", None))
#if QT_CONFIG(tooltip)
        self.Account_list.setToolTip(QCoreApplication.translate("assignment_window", u"<html><head/><body><p>\ub354\ube14 \ud074\ub9ad\uc2dc \uad00\ub9ac\uc790 \uad8c\ud55c\uc744 </p><p>\ubd80\uc5ec/\uc0ad\uc81c \uac00\ub2a5\ud569\ub2c8\ub2e4.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("assignment_window", u"\uacc4\uc815 \ubaa9\ub85d", None))
    # retranslateUi

