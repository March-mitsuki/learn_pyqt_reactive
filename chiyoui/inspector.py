from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QDialog,
    QFrame,
)
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QCursor
import sys


class InspectorDialog(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Inspector")
        self.setGeometry(600, 100, 300, 200)

        # 保存主窗口引用
        self.main_window = main_window
        self.prev_widget = None
        self.prev_widget_style = None

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

        # 创建一个覆盖层来展示边距和间距
        self.overlay_frame = QFrame(self.main_window)
        self.overlay_frame.setStyleSheet("background: rgba(0, 255, 0, 0.3);")
        self.overlay_frame.hide()  # 初始状态为隐藏

    def start_inspecting(self):
        # 开始定时检测，并捕获鼠标
        self.timer.start(100)
        self.inspect_button.setEnabled(False)
        self.grabMouse()  # 捕获鼠标事件

    def highlight_widget_under_cursor(self):
        # 使用 QCursor 获取全局鼠标位置并转换为主窗口坐标
        cursor_pos = self.main_window.mapFromGlobal(QCursor.pos())
        widget = self.main_window.childAt(cursor_pos)

        # 如果鼠标下的组件与前一个组件不同，进行高亮更新
        if widget and widget != self.prev_widget:
            # 重置前一个组件的背景颜色
            if self.prev_widget:
                self.prev_widget.setStyleSheet(self.prev_widget_style)

            # 设置当前组件的背景颜色为黄色
            self.prev_widget_style = widget.styleSheet()
            self.prev_widget = widget
            widget.setStyleSheet("background-color: yellow;")

            # 更新 InspectorDialog 中的组件信息，包括边距和间距
            layout = widget.layout()
            margin_info = ""
            spacing_info = ""
            if layout:
                margins = layout.contentsMargins()
                margin_info = f"Margins: left={margins.left()}, top={margins.top()}, right={margins.right()}, bottom={margins.bottom()}"
                spacing_info = f"Spacing: {layout.spacing()}"

                # 获取组件的全局位置并展示可视化的边距和间距
                widget_rect = widget.geometry()
                widget_rect = QRect(
                    widget.mapTo(self.main_window, widget_rect.topLeft()),
                    widget_rect.size(),
                )

                # 设置覆盖框的位置和大小
                self.overlay_frame.setGeometry(
                    widget_rect.adjusted(
                        -margins.left(),
                        -margins.top(),
                        margins.right(),
                        margins.bottom(),
                    )
                )
                self.overlay_frame.show()

            self.info_label.setText(
                f"Inspecting: {widget.objectName() or 'Unnamed Widget'}\n{margin_info}\n{spacing_info}"
            )

    def mousePressEvent(self, event):
        # 监听鼠标左键，按下左键则结束检查
        if event.button() == Qt.MouseButton.LeftButton:
            self.stop_inspecting()

    def stop_inspecting(self):
        # 停止检查，释放鼠标，并重置组件颜色
        self.timer.stop()
        self.releaseMouse()  # 释放鼠标捕获
        if self.prev_widget:
            self.prev_widget.setStyleSheet(self.prev_widget_style)
        self.overlay_frame.hide()  # 隐藏覆盖框
        self.inspect_button.setEnabled(True)


if __name__ == "__main__":
    """主窗口示例"""

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
