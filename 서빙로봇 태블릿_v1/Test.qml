import QtQuick 2.15
import QtQuick.Controls 2.15
from qmltest import Main
ApplicationWindow {
    visible: true
    width: 400
    height: 200

    Rectangle {
        width: parent.width
        height: parent.height

        Button {
            text: "클릭하세요"
            anchors.centerIn: parent

            onClicked: {
                // Python 함수 호출
                myPythonFunction()
            }
        }
    }
}
