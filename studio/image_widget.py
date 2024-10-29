from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QPainter, QBrush
from PyQt6.QtCore import Qt, QPointF


class ImageWidget(QLabel):
    def __init__(self, img_path, parent):
        super().__init__()
        pixmap = QPixmap(img_path)
        if pixmap.isNull():
            self.setText("Image not found")
            return
        img_w = pixmap.width()
        img_h = pixmap.height()
        if pixmap.width() > parent.width() or pixmap.height() > parent.height():
            img_w = int(parent.width() * 0.9)
            img_h = int(parent.height() * 0.9)
            pixmap = pixmap.scaled(
                img_w,
                img_h,
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation,
            )
        self.setFixedSize(pixmap.size())
        self.setPixmap(pixmap)


class ClickPercentImageWidget(ImageWidget):
    def __init__(
        self,
        img_path,
        click_percent_x,
        click_percent_y,
        parent,
    ):
        self.click_percent_x = click_percent_x
        self.click_percent_y = click_percent_y
        super().__init__(img_path, parent)

        self.rect_size = 10
        self.rect_pos = QPointF(
            self.width() * self.click_percent_x,
            self.height() * self.click_percent_y,
        )

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setBrush(QBrush(Qt.GlobalColor.green))
        painter.drawRect(
            int(self.rect_pos.x() - self.rect_size / 2),
            int(self.rect_pos.y() - self.rect_size / 2),
            self.rect_size,
            self.rect_size,
        )
