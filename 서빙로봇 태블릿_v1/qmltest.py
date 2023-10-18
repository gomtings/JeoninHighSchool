"""
Main 
"""
from PyQt5.QtGui  import QGuiApplication
from PyQt5.QtQml  import QQmlApplicationEngine
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import sys

class Main(QObject): 
    def __init__(self):
        QObject.__init__(self)
    def myPythonFunction(self):
        print("버튼 클릭")

if __name__ == "__main__":
    app    = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    main   = Main()
   # engine.rootContext().setContextProperty("TestForm", main)
    engine.load("Test.qml")
    engine.quit.connect(app.quit)
    sys.exit(app.exec_())
