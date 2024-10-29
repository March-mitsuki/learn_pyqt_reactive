from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush, QFontMetrics
from PyQt6.QtCore import Qt, QPointF, QRectF, QSizeF
import sys


class DraggableRectangleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.rect_size = 10  # 矩形的大小
        self.rect_pos = QPointF(100, 100)  # 初始矩形中心位置
        self.dragging = False  # 用于判断是否在拖动矩形

    def mousePressEvent(self, event):
        # 判断是否点击在矩形内
        rect_top_left = QPointF(
            self.rect_pos.x() - self.rect_size / 2,
            self.rect_pos.y() - self.rect_size / 2,
        )
        if QRectF(rect_top_left, QSizeF(self.rect_size, self.rect_size)).contains(
            event.position()
        ):
            self.dragging = True
            self.offset = (
                event.position() - self.rect_pos
            )  # 记录点击位置与矩形中心的偏移量

    def mouseMoveEvent(self, event):
        if self.dragging:
            # 更新矩形位置，使其中心位置跟随鼠标
            self.rect_pos = event.position() - self.offset
            self.update()  # 刷新界面

    def mouseReleaseEvent(self, event):
        # 结束拖动
        self.dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 获取窗口的宽高
        width, height = self.width(), self.height()

        # 计算矩形的相对位置，以中心为基准
        relative_x = self.rect_pos.x() / width
        relative_y = self.rect_pos.y() / height

        # 绘制矩形框，注意以中心位置为基准绘制
        painter.setBrush(QBrush(Qt.GlobalColor.blue))
        rect_x = int(self.rect_pos.x() - self.rect_size / 2)
        rect_y = int(self.rect_pos.y() - self.rect_size / 2)
        painter.drawRect(QRectF(rect_x, rect_y, self.rect_size, self.rect_size))

        # 绘制连线
        pen = QPen(Qt.GlobalColor.red, 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        center_y = int(rect_y + self.rect_size / 2)
        center_x = int(rect_x + self.rect_size / 2)
        painter.drawLine(0, center_y, rect_x, center_y)  # 左边连线
        painter.drawLine(center_x, 0, center_x, rect_y)  # 上边连线

        # 显示矩形相对位置百分比
        painter.setPen(Qt.GlobalColor.black)
        pos_text = f"({relative_x:.2f}, {relative_y:.2f})"
        text_width = QFontMetrics(painter.font()).horizontalAdvance(pos_text)
        text_height = QFontMetrics(painter.font()).height()
        painter.drawText(
            int(self.rect_pos.x() - text_width / 2),
            int(self.rect_pos.y() + text_height),
            pos_text,
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DraggableRectangleWidget()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())
