# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Day1_wordlist.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
from PySide6.QtWidgets import (QApplication, QDialog, QHeaderView, QPushButton,
    QSizePolicy, QTableWidget, QTableWidgetItem, QWidget)

class wordlist_ui1(object):
    def setupUi(self, Day1):
        if not Day1.objectName():
            Day1.setObjectName(u"Day1")
        Day1.resize(423, 357)
        self.tableWidget = QTableWidget(Day1)
        if (self.tableWidget.columnCount() < 2):
            self.tableWidget.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        if (self.tableWidget.rowCount() < 10):
            self.tableWidget.setRowCount(10)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(3, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(4, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(5, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(6, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(7, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(8, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(9, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableWidget.setItem(0, 0, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableWidget.setItem(0, 1, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tableWidget.setItem(1, 0, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tableWidget.setItem(1, 1, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.tableWidget.setItem(2, 0, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.tableWidget.setItem(2, 1, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.tableWidget.setItem(3, 0, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        self.tableWidget.setItem(3, 1, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        self.tableWidget.setItem(4, 0, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        self.tableWidget.setItem(4, 1, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        self.tableWidget.setItem(5, 0, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        self.tableWidget.setItem(5, 1, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        self.tableWidget.setItem(6, 0, __qtablewidgetitem24)
        __qtablewidgetitem25 = QTableWidgetItem()
        self.tableWidget.setItem(6, 1, __qtablewidgetitem25)
        __qtablewidgetitem26 = QTableWidgetItem()
        self.tableWidget.setItem(7, 0, __qtablewidgetitem26)
        __qtablewidgetitem27 = QTableWidgetItem()
        self.tableWidget.setItem(7, 1, __qtablewidgetitem27)
        __qtablewidgetitem28 = QTableWidgetItem()
        self.tableWidget.setItem(8, 0, __qtablewidgetitem28)
        __qtablewidgetitem29 = QTableWidgetItem()
        self.tableWidget.setItem(8, 1, __qtablewidgetitem29)
        __qtablewidgetitem30 = QTableWidgetItem()
        self.tableWidget.setItem(9, 0, __qtablewidgetitem30)
        __qtablewidgetitem31 = QTableWidgetItem()
        self.tableWidget.setItem(9, 1, __qtablewidgetitem31)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(50, 10, 401, 331))
        self.pushButton = QPushButton(Day1)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(300, 40, 101, 20))

        self.retranslateUi(Day1)

        QMetaObject.connectSlotsByName(Day1)
    # setupUi

    def retranslateUi(self, Day1):
        Day1.setWindowTitle(QCoreApplication.translate("Day1", u"Dialog", None))
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Day1", u"\ub2e8\uc5b4", None));
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Day1", u"\ub73b", None));
        ___qtablewidgetitem2 = self.tableWidget.verticalHeaderItem(0)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Day1", u"1.", None));
        ___qtablewidgetitem3 = self.tableWidget.verticalHeaderItem(1)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Day1", u"2.", None));
        ___qtablewidgetitem4 = self.tableWidget.verticalHeaderItem(2)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Day1", u"3.", None));
        ___qtablewidgetitem5 = self.tableWidget.verticalHeaderItem(3)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Day1", u"4.", None));
        ___qtablewidgetitem6 = self.tableWidget.verticalHeaderItem(4)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("Day1", u"5.", None));
        ___qtablewidgetitem7 = self.tableWidget.verticalHeaderItem(5)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("Day1", u"6.", None));
        ___qtablewidgetitem8 = self.tableWidget.verticalHeaderItem(6)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("Day1", u"7.", None));
        ___qtablewidgetitem9 = self.tableWidget.verticalHeaderItem(7)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("Day1", u"8.", None));
        ___qtablewidgetitem10 = self.tableWidget.verticalHeaderItem(8)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("Day1", u"9.", None));
        ___qtablewidgetitem11 = self.tableWidget.verticalHeaderItem(9)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("Day1", u"10.", None));

        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        ___qtablewidgetitem12 = self.tableWidget.item(0, 0)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("Day1", u"Apple", None));
        ___qtablewidgetitem13 = self.tableWidget.item(0, 1)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("Day1", u"\uc0ac\uacfc", None));
        ___qtablewidgetitem14 = self.tableWidget.item(1, 0)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("Day1", u"pineapple", None));
        ___qtablewidgetitem15 = self.tableWidget.item(1, 1)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("Day1", u"\ud30c\uc778\uc560\ud50c", None));
        ___qtablewidgetitem16 = self.tableWidget.item(2, 0)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("Day1", u"kiwi", None));
        ___qtablewidgetitem17 = self.tableWidget.item(2, 1)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("Day1", u"\ud0a4\uc704", None));
        ___qtablewidgetitem18 = self.tableWidget.item(3, 0)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("Day1", u"orange", None));
        ___qtablewidgetitem19 = self.tableWidget.item(3, 1)
        ___qtablewidgetitem19.setText(QCoreApplication.translate("Day1", u"\uc624\ub80c\uc9c0", None));
        ___qtablewidgetitem20 = self.tableWidget.item(4, 0)
        ___qtablewidgetitem20.setText(QCoreApplication.translate("Day1", u"egg", None));
        ___qtablewidgetitem21 = self.tableWidget.item(4, 1)
        ___qtablewidgetitem21.setText(QCoreApplication.translate("Day1", u"\uacc4\ub780", None));
        ___qtablewidgetitem22 = self.tableWidget.item(5, 0)
        ___qtablewidgetitem22.setText(QCoreApplication.translate("Day1", u"sangchu", None));
        ___qtablewidgetitem23 = self.tableWidget.item(5, 1)
        ___qtablewidgetitem23.setText(QCoreApplication.translate("Day1", u"\uc0c1\ucd94", None));
        ___qtablewidgetitem24 = self.tableWidget.item(6, 0)
        ___qtablewidgetitem24.setText(QCoreApplication.translate("Day1", u"robot", None));
        ___qtablewidgetitem25 = self.tableWidget.item(6, 1)
        ___qtablewidgetitem25.setText(QCoreApplication.translate("Day1", u"\ub85c\ubd07", None));
        ___qtablewidgetitem26 = self.tableWidget.item(7, 0)
        ___qtablewidgetitem26.setText(QCoreApplication.translate("Day1", u"ticks", None));
        ___qtablewidgetitem27 = self.tableWidget.item(7, 1)
        ___qtablewidgetitem27.setText(QCoreApplication.translate("Day1", u"\ud2f1\uc2a4", None));
        ___qtablewidgetitem28 = self.tableWidget.item(8, 0)
        ___qtablewidgetitem28.setText(QCoreApplication.translate("Day1", u"table", None));
        ___qtablewidgetitem29 = self.tableWidget.item(8, 1)
        ___qtablewidgetitem29.setText(QCoreApplication.translate("Day1", u"\ucc45\uc0c1", None));
        ___qtablewidgetitem30 = self.tableWidget.item(9, 0)
        ___qtablewidgetitem30.setText(QCoreApplication.translate("Day1", u"chair", None));
        ___qtablewidgetitem31 = self.tableWidget.item(9, 1)
        ___qtablewidgetitem31.setText(QCoreApplication.translate("Day1", u"\uc758\uc790", None));
        self.tableWidget.setSortingEnabled(__sortingEnabled)

        self.pushButton.setText(QCoreApplication.translate("Day1", u"\ub098\uac00\uae30", None))
    # retranslateUi

