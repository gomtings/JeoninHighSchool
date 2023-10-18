import sys

from PyQt5 import QtCore, QtGui, QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tabwidget = QtWidgets.QTabWidget()
        self.tabwidget.addTab(QtWidgets.QWidget(), "Tab1")
        self.tabwidget.addTab(QtWidgets.QWidget(), "Tab2")
        self.tabwidget.addTab(QtWidgets.QWidget(), "Tab3")

        self.setCentralWidget(self.tabwidget)

        self.tabwidget.tabBarClicked.connect(self.handle_tabbar_clicked)

    def handle_tabbar_clicked(self, index):
        print(index)

        print("x2:", index * 2)


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    w = MainWindow()
    w.show()

    sys.exit(app.exec_())