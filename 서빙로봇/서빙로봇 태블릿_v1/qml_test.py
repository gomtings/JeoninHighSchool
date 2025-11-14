from PyQt5.QtGui  import QGuiApplication
from PyQt5.QtQml  import QQmlApplicationEngine
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import os
import sys

app = QGuiApplication(sys.argv)
view = QQuickView()
view.setResizeMode(QQuickView.SizeRootObjectToView)
current_path = os.path.abspath(os.path.dirname(__file__))
qml_file = os.path.join(current_path, 'app.qml')
view.setSource(QUrl.fromLocalFile(qmlFile))
if view.status() == QQuickView.Error:
    sys.exit(-1)