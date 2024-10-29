from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QRect, QSize, QPoint, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QPainter


class ScreenshotWidget(QWidget):
    """
    Starts a full-screen screenshot selection widget.

    When the user selects a region, the `on_screenshot_captured` signal is emitted,
    passing the selected screenshot as a QPixmap object.

    And then the widget will close itself.
    """

    on_screenshot_captured = pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 计算所有屏幕的总几何区域，并设置窗口大小
        self.total_geometry = self.calculate_total_geometry()
        self.setGeometry(self.total_geometry)

        # 获取所有屏幕截图并合并
        self.screenshot = self.capture_all_screens()

        # 创建灰色覆盖图层
        self.gray_overlay = self.apply_gray_overlay(self.screenshot.copy())

        # 初始化选择框区域
        self.origin = None
        self.selection_rect = QRect()

        self.setMouseTracking(True)

    def calculate_total_geometry(self):
        """计算所有屏幕的总几何区域"""
        screens = QApplication.screens()
        total_geometry = QRect()

        # 计算总的屏幕几何范围
        for screen in screens:
            total_geometry = total_geometry.united(screen.geometry())
        return total_geometry

    def capture_all_screens(self):
        """捕获所有屏幕并合并成一张图片"""
        screens = QApplication.screens()
        combined_pixmap = QPixmap(self.total_geometry.size())
        combined_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(combined_pixmap)
        for screen in screens:
            pixmap = screen.grabWindow(0)
            # 计算屏幕的偏移（相对整个几何区域）
            offset = screen.geometry().topLeft() - self.total_geometry.topLeft()
            painter.drawPixmap(offset, pixmap)
        painter.end()

        return combined_pixmap

    def apply_gray_overlay(self, pixmap):
        """创建一个带灰色覆盖的副本"""
        overlay = QPixmap(pixmap.size())
        overlay.fill(QColor(0, 0, 0, 128))  # 半透明灰色
        painter = QPainter(pixmap)
        painter.drawPixmap(0, 0, overlay)
        painter.end()
        return pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.gray_overlay)
        if not self.selection_rect.isNull():
            painter.setPen(QColor(0, 255, 0))
            painter.drawRect(
                QRect(
                    QPoint(
                        self.selection_rect.topLeft().x() - 1,
                        self.selection_rect.topLeft().y() - 1,
                    ),
                    self.selection_rect.size() + QSize(1, 1),
                )
            )
            painter.drawPixmap(
                self.selection_rect, self.screenshot.copy(self.selection_rect)
            )
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 使用相对于窗口的本地坐标，因窗口覆盖整个屏幕
            self.origin = event.pos()  # 相对于窗口的坐标
            self.selection_rect = QRect(self.origin, QSize())
            self.update()

    def mouseMoveEvent(self, event):
        if self.origin:
            # 直接使用鼠标相对窗口的本地坐标
            self.selection_rect = QRect(self.origin, event.pos()).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            screenshot = self.take_screenshot()
            self.on_screenshot_captured.emit(screenshot)
            self.close()

    def take_screenshot(self):
        geometry = self.selection_rect
        screenshot = self.screenshot.copy(geometry)
        return screenshot
