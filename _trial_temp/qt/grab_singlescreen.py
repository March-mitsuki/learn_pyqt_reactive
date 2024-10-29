import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QRect, QSize, QPoint
from PyQt6.QtGui import QPixmap, QColor, QPainter


class ScreenshotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 对整个屏幕截图
        screen = QApplication.primaryScreen()
        self.screenshot = screen.grabWindow(0)  # 原始截图

        # 创建灰色覆盖图层
        self.gray_overlay = self.applyGrayOverlay(
            self.screenshot.copy()
        )  # 使用截图的副本

        # 初始化选择框区域
        self.origin = None
        self.selection_rect = QRect()

        self.setMouseTracking(True)

    def applyGrayOverlay(self, pixmap):
        """创建一个带灰色覆盖的副本"""
        overlay = QPixmap(pixmap.size())
        overlay.fill(QColor(0, 0, 0, 128))  # 半透明灰色
        painter = QPainter(pixmap)
        painter.drawPixmap(0, 0, overlay)  # 将灰色蒙层绘制在截图副本上
        painter.end()
        return pixmap  # 返回带灰色蒙层的副本

    def paintEvent(self, event):
        painter = QPainter(self)

        # 绘制灰色覆盖
        painter.drawPixmap(0, 0, self.gray_overlay)

        # 如果选择框正在被绘制
        if not self.selection_rect.isNull():
            # 绘制绿色选择框
            painter.setPen(QColor(0, 255, 0))  # 绿色边框
            painter.drawRect(
                QRect(
                    QPoint(
                        self.selection_rect.topLeft().x() - 1,
                        self.selection_rect.topLeft().y() - 1,
                    ),
                    self.selection_rect.size() + QSize(1, 1),
                )
            )

            # 显示选取区域内的部分（从灰色中移除灰色蒙层，显示原始截图）
            painter.drawPixmap(
                self.selection_rect, self.screenshot.copy(self.selection_rect)
            )

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.pos()
            self.selection_rect = QRect(self.origin, QSize())
            self.update()

    def mouseMoveEvent(self, event):
        if self.origin:
            self.selection_rect = QRect(self.origin, event.pos()).normalized()
            self.update()  # 刷新界面，更新选择区域

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.takeScreenshot()
            self.selection_rect = QRect()  # 清除选择框
            self.update()
            QApplication.quit()  # 截图完成后退出应用程序

    def takeScreenshot(self):
        geometry = self.selection_rect
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(
            0, geometry.x(), geometry.y(), geometry.width(), geometry.height()
        )
        screenshot.save("screenshot.png", "png")
        print("Screenshot saved: screenshot.png")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenshotWidget()
    window.show()
    sys.exit(app.exec())
