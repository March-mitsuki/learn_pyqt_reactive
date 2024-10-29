from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush
from PyQt6.QtCore import Qt, QPointF, QRectF
import sys


class MousePositionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(
            True
        )  # 开启鼠标追踪，不需要按下按钮才能触发mouseMoveEvent
        self.mouse_pos = QPointF(0, 0)  # 初始化鼠标位置

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.position()  # 更新鼠标位置
        self.update()  # 刷新界面

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 获取窗口的宽高
        width, height = self.width(), self.height()

        # 计算相对位置
        relative_x = self.mouse_pos.x() / width
        relative_y = self.mouse_pos.y() / height

        # 绘制矩形框
        rect_size = 10  # 矩形框的大小
        rect_x = int(self.mouse_pos.x() - rect_size / 2)
        rect_y = int(self.mouse_pos.y() - rect_size / 2)
        painter.setBrush(QBrush(Qt.GlobalColor.blue))
        painter.drawRect(QRectF(rect_x, rect_y, rect_size, rect_size))

        # 绘制连线
        pen = QPen(Qt.GlobalColor.red, 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        moust_y = int(self.mouse_pos.y())
        moust_x = int(self.mouse_pos.x())
        painter.drawLine(0, moust_y, moust_x, moust_y)  # 左边连线
        painter.drawLine(moust_x, 0, moust_x, moust_y)  # 上边连线

        # 显示相对位置百分比
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(
            rect_x + rect_size,
            rect_y + rect_size,
            f"({relative_x:.2%}, {relative_y:.2%})",
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MousePositionWidget()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())
