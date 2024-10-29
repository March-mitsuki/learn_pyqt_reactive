from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QDialog,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor
import sys


class InspectorDialog(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Inspector")
        self.setGeometry(600, 100, 300, 200)

        # 保存主窗口引用
        self.main_window = main_window
        self.previous_widget = None

        # 布局和开始检查按钮
        layout = QVBoxLayout()
        self.inspect_button = QPushButton("Start Inspect")
        self.inspect_button.clicked.connect(self.start_inspecting)
        layout.addWidget(self.inspect_button)

        self.info_label = QLabel("Hover over elements to inspect.")
        layout.addWidget(self.info_label)
        self.setLayout(layout)

        # 定时器用于检测鼠标下的组件
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.highlight_widget_under_cursor)

        # 创建提示框
        self.overlay = QWidget(self.main_window)
        self.overlay.setWindowFlags(Qt.WindowType.ToolTip)  # 防止阻挡鼠标事件
        self.overlay.setStyleSheet(
            "background-color: rgba(255, 255, 0, 0.3);"
        )  # 半透明黄色
        self.overlay.hide()

    def start_inspecting(self):
        # 开始定时检测
        self.timer.start(100)
        self.inspect_button.setEnabled(False)

    def highlight_widget_under_cursor(self):
        # 获取鼠标在主窗口内的相对坐标
        cursor_pos = self.main_window.mapFromGlobal(QCursor.pos())
        widget = self.main_window.childAt(cursor_pos)

        # 如果鼠标下的组件与前一个组件不同，进行高亮更新
        if widget and widget != self.previous_widget:
            # 更新提示框的位置和大小
            widget_rect = widget.geometry()
            # 设置提示框为组件的位置与大小
            self.overlay.setGeometry(
                widget.mapTo(self.main_window, widget_rect.topLeft()).x(),
                widget.mapTo(self.main_window, widget_rect.topLeft()).y(),
                widget_rect.width(),
                widget_rect.height(),
            )
            self.overlay.show()
            self.previous_widget = widget

            # 在 InspectorDialog 中更新组件信息
            self.info_label.setText(
                f"Inspecting: {widget.objectName() or 'Unnamed Widget'}"
            )

    def mousePressEvent(self, event):
        # 监听鼠标左键，按下左键则结束检查
        if event.button() == Qt.MouseButton.LeftButton:
            self.stop_inspecting()

    def stop_inspecting(self):
        # 停止检查，隐藏提示框
        self.timer.stop()
        self.overlay.hide()
        self.info_label.setText("Inspection completed.")
        self.inspect_button.setEnabled(True)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 400, 300)

        # 主窗口布局和测试标签
        layout = QVBoxLayout()
        for i in range(5):
            label = QLabel(f"Label {i+1}", self)
            label.setObjectName(f"label_{i+1}")
            label.setStyleSheet("background-color: lightgray;")
            layout.addWidget(label)

        # 添加检查器按钮
        self.inspect_button = QPushButton("Open Inspector", self)
        self.inspect_button.clicked.connect(self.open_inspector)
        layout.addWidget(self.inspect_button)

        self.setLayout(layout)

    def open_inspector(self):
        # 创建并显示检查器对话框
        self.inspector = InspectorDialog(self)
        self.inspector.show()


# 运行应用程序
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
