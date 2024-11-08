from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QMessageBox
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QListWidget Example with PySide6")
        
        # 레이아웃 생성
        layout = QVBoxLayout()
        
        # QListWidget 생성
        self.list_widget = QListWidget()
        
        # 기본 항목 추가
        self.list_widget.addItem("Apple")
        self.list_widget.addItem("Banana")
        self.list_widget.addItem("Cherry")
        
        # 항목 추가 버튼
        add_button = QPushButton("Add Item")
        add_button.clicked.connect(self.add_item)
        
        # 항목 삭제 버튼
        delete_button = QPushButton("Delete Selected Item")
        delete_button.clicked.connect(self.delete_item)
        
        # 선택된 항목 출력 버튼
        show_button = QPushButton("Show Selected Item")
        show_button.clicked.connect(self.show_selected_item)
        
        # 레이아웃에 위젯 추가
        layout.addWidget(self.list_widget)
        layout.addWidget(add_button)
        layout.addWidget(delete_button)
        layout.addWidget(show_button)
        
        self.setLayout(layout)

    # 항목 추가 메서드
    def add_item(self):
        new_item = QListWidgetItem("New Item")
        self.list_widget.addItem(new_item)
    
    # 선택된 항목 삭제 메서드
    def delete_item(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.list_widget.takeItem(current_row)
    
    # 선택된 항목 출력 메서드
    def show_selected_item(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            QMessageBox.information(self, "Selected Item", f"You selected: {selected_item.text()}")
        else:
            QMessageBox.information(self, "Selected Item", "No item selected.")

# 실행 코드
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
