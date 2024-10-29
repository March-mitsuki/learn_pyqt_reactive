from PyQt6.QtWidgets import (
    QDialog,
    QApplication,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QMessageBox,
    QCheckBox,
)
from PyQt6.QtGui import QPixmap, QPainter, QPen, QBrush, QFontMetrics
from PyQt6.QtCore import Qt, QPointF, QRectF, QSizeF, pyqtSignal
from loguru import logger
from pathlib import Path

from .utils import (
    zoom_rect,
    make_screen_img_path,
    make_click_img_path,
    make_percent_match_img_path,
)
from .form_controls import InputForm, SelectForm
from .screenshot import ScreenshotWidget
from db.models import Operation, Task, OperationType
from settings import MATCH_IMG_DIR


class PercentDialog(QWidget):
    on_percent_selected = pyqtSignal((float, float))

    def __init__(self, screenshot: QPixmap, percent: tuple[float, float]):
        self.screenshot = screenshot
        super().__init__()

        # 设置窗口大小为截图大小
        self.setWindowTitle("Select Point")
        self.setGeometry(screenshot.rect())

        init_x = percent[0] * self.width()
        init_y = percent[1] * self.height()
        self.rect_size = 10  # 矩形的大小
        self.rect_pos = QPointF(init_x, init_y)  # 初始矩形中心位置
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
        painter.drawPixmap(0, 0, self.screenshot)

        # 获取窗口的宽高
        width, height = self.width(), self.height()

        # 计算矩形的相对位置，以中心为基准
        relative_x = self.rect_pos.x() / width
        relative_y = self.rect_pos.y() / height

        # 绘制矩形框，注意以中心位置为基准绘制
        painter.setBrush(QBrush(Qt.GlobalColor.green))
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
        text_x = int(self.rect_pos.x() - text_width / 2)
        text_y = int(self.rect_pos.y() + text_height + 10)
        text_background = QRectF(
            text_x - 5,
            text_y - text_height + 2,
            text_width + 10,
            text_height + 4,
        )
        painter.fillRect(text_background, Qt.GlobalColor.white)
        painter.drawText(
            text_x,
            text_y,
            pos_text,
        )

        self.on_percent_selected.emit(
            round(relative_x, 2),
            round(relative_y, 2),
        )


class PercentSelector(QWidget):
    on_percent_selected = pyqtSignal((float, float))

    def __init__(self, screenshot: QPixmap):
        self.screenshot = screenshot
        self._init_percent()
        super().__init__()

        self.btn = QPushButton("Select Point")
        self.btn.clicked.connect(self.open_dialog)
        self.percent_review = QLabel(self.get_percent_str())

        layout = QVBoxLayout()
        layout.addWidget(self.btn)
        layout.addWidget(self.percent_review)

        self.setLayout(layout)

    def _init_percent(self):
        self.percent_x = 0.1
        self.percent_y = 0.1

    def get_percent(self):
        return (self.percent_x, self.percent_y)

    def get_percent_str(self):
        return f"Click Percent: ({self.percent_x:.2f}, {self.percent_y:.2f})"

    def open_dialog(self):
        self.dialog = PercentDialog(self.screenshot, self.get_percent())
        self.dialog.on_percent_selected.connect(self.handle_percent_selected)
        self.dialog.show()

    def handle_percent_selected(self, percent_x, percent_y):
        self.percent_x = percent_x
        self.percent_y = percent_y
        self.percent_review.setText(self.get_percent_str())
        self.on_percent_selected.emit(percent_x, percent_y)


class ImgSelector(QWidget):
    on_grab_screen = pyqtSignal(QPixmap)

    def __init__(self, btn_text="Grab Screen"):
        super().__init__()

        self.grab_screen_btn = QPushButton(btn_text)
        self.grab_screen_btn.clicked.connect(self.start_grab_screen)

        self.screenshot_review = QLabel(self)
        self.screenshot_review.hide()

        layout = QVBoxLayout()
        layout.addWidget(self.grab_screen_btn)
        layout.addWidget(self.screenshot_review)

        self.setLayout(layout)

    def start_grab_screen(self):
        self.screenshot_window = ScreenshotWidget()
        self.screenshot_window.on_screenshot_captured.connect(
            self.handle_screenshot_captured
        )
        self.screenshot_window.show()

    def handle_screenshot_captured(self, screenshot):
        self.on_grab_screen.emit(screenshot)
        self.screenshot_review.setPixmap(screenshot)
        self.screenshot_review.show()


class OperationEditor(QDialog):
    """
    Will close itself after operation saved
    """

    on_operation_saved = pyqtSignal(Operation)

    def __init__(self, task: Task, screenshot: QPixmap):
        self.task = task
        self.screenshot = screenshot.copy()  # 保留原始截图
        self._init_selectors()
        self.click_img = None
        self.click_percent_x = None
        self.click_percent_y = None
        self.click_percent_match_img = None
        self.click_times = 1
        self.wait_timeout = 120
        self.is_implicity_wait = False
        self.operation_name = None
        super().__init__()

        self.setWindowTitle("Operation Editor")
        screen_geom = QApplication.primaryScreen().geometry()
        self.setGeometry(zoom_rect(screen_geom, 0.7))

        self.screenshot_label = QLabel(self)

        self.screenshot_label.setPixmap(
            screenshot.scaled(
                int(self.width() * 0.5),
                int(self.height() * 0.5),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation,
            )
        )

        left_content = QVBoxLayout()
        left_content.addWidget(QLabel("Screen image"))
        left_content.addWidget(self.screenshot_label)
        left_content.addWidget(self.img_selector)
        left_content.addWidget(self.percent_selector)

        self.operation_name_input = InputForm("Operatiion Name", "Enter operation name")
        self.operation_name_input.on_change.connect(self.handle_operation_name_change)

        self.click_times_input = InputForm("Click Times", "Enter click times")
        self.click_times_input.on_change.connect(self.handle_click_times_change)

        self.wait_timeout_input = InputForm("Wait Timeout (s)", "Enter wait timeout")
        self.wait_timeout_input.on_change.connect(self.handle_wait_timeout_change)
        self.wait_timeout_input.hide()

        self.implicity_wait_check_box = QCheckBox("Is Implicity Wait")
        self.implicity_wait_check_box.toggled.connect(self.handle_implicity_wait_change)
        self.implicity_wait_check_box.hide()

        operation_types = OperationType.to_list()
        self.operation_type_select = SelectForm("Operation Type", operation_types)
        self.operation_type_select.on_change.connect(self.handle_operation_type_change)
        self.operation_type = operation_types[0]
        self.handle_operation_type_change(
            self.operation_type
        )  # set default operation type

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.submit)

        right_content = QVBoxLayout()
        right_content.addWidget(self.operation_type_select)
        right_content.addWidget(self.operation_name_input)
        right_content.addWidget(self.click_times_input)
        right_content.addWidget(self.wait_timeout_input)
        right_content.addWidget(self.implicity_wait_check_box)
        right_content.addWidget(self.percent_match_img_selector)
        right_content.addWidget(self.submit_btn)

        hbox = QHBoxLayout()
        hbox.addLayout(left_content)
        hbox.addLayout(right_content)

        self.setLayout(hbox)

    def _init_selectors(self):
        self.img_selector = ImgSelector("Grab click image")
        self.img_selector.on_grab_screen.connect(self.handle_img_selected)
        self.img_selector.hide()

        self.percent_selector = PercentSelector(self.screenshot)
        self.percent_selector.on_percent_selected.connect(self.handle_percent_selected)
        self.percent_selector.hide()

        self.percent_match_img_selector = ImgSelector("Grab click percent match image")
        self.percent_match_img_selector.on_grab_screen.connect(
            self.handle_percent_match_img_selected
        )
        self.percent_match_img_selector.hide()

    def handle_implicity_wait_change(self):
        self.is_implicity_wait = self.implicity_wait_check_box.isChecked()

    def handle_percent_match_img_selected(self, screenshot):
        self.click_percent_match_img = screenshot

    def handle_click_times_change(self, text):
        if not text:
            self.click_times = 1
            return
        self.click_times = int(text)

    def handle_wait_timeout_change(self, text):
        self.wait_timeout = text

    def handle_operation_name_change(self, text):
        self.operation_name = text

    def handle_operation_type_change(self, operation_type):
        self.operation_type = operation_type
        if self.operation_type == "click_img":
            self.click_times_input.show()

            self.img_selector.show()

            self.percent_selector.hide()
            self.percent_match_img_selector.hide()

            self.wait_timeout_input.hide()
            self.implicity_wait_check_box.hide()

        elif self.operation_type == "click_percent":
            self.click_times_input.show()

            self.img_selector.hide()

            self.percent_selector.show()
            self.percent_match_img_selector.show()

            self.wait_timeout_input.hide()
            self.implicity_wait_check_box.hide()

        elif self.operation_type == "wait":
            self.click_times_input.hide()

            self.img_selector.hide()

            self.percent_selector.hide()
            self.percent_match_img_selector.hide()

            self.wait_timeout_input.show()
            self.implicity_wait_check_box.show()

    def handle_img_selected(self, screenshot):
        self.click_img = screenshot

    def handle_percent_selected(self, percent_x, percent_y):
        self.click_percent_x = percent_x
        self.click_percent_y = percent_y

    def submit(self):
        if not self.operation_name:
            QMessageBox.critical(self, "Error", "Operation name is required")
            return
        if self.click_times < 1 or not isinstance(self.click_times, int):
            QMessageBox.critical(
                self, "Error", "Click times must be a positive integer"
            )
            return

        self.check_dir_exist(MATCH_IMG_DIR)
        screen_img_path = make_screen_img_path(self.operation_name, as_str=True)
        ok = self.screenshot.save(screen_img_path)
        if not ok:
            raise Exception("Failed to save screen image")

        click_img_path = None
        if self.click_img:
            click_img_path = make_click_img_path(self.operation_name, as_str=True)
            ok = self.click_img.save(click_img_path)
            if not ok:
                raise Exception("Failed to save click image")

        percent_match_img_path = None
        if self.click_percent_match_img:
            percent_match_img_path = make_percent_match_img_path(
                self.operation_name, as_str=True
            )
            ok = self.click_percent_match_img.save(percent_match_img_path)
            if not ok:
                raise Exception("Failed to save percent match image")

        try:
            operation = Operation.create(
                name=self.operation_name,
                operation_type=self.operation_type,
                screen_img=screen_img_path,
                click_img=click_img_path,
                click_percent_x=self.click_percent_x,
                click_percent_y=self.click_percent_y,
                click_percent_match_img=percent_match_img_path,
                click_times=self.click_times,
                wait_timeout=self.wait_timeout,
                is_implicity_wait=self.is_implicity_wait,
                task=self.task,
            )
            self.on_operation_saved.emit(operation)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to save operation")
            logger.exception("Failed to save operation: {}", e)

    def check_dir_exist(self, dir_path):
        if not isinstance(dir_path, Path):
            dir_path = Path(dir_path)
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
