from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QMessageBox,
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import pyqtSignal


from db.models import Task, Operation, OperationType
from .operation_editor import OperationEditor
from .screenshot import ScreenshotWidget
from .utils import clear_layout
from .dnd_widget import DragItemContainer, DragWidget
from .image_widget import ImageWidget, ClickPercentImageWidget


class OperationView(QWidget):
    def __init__(self, operation: Operation):
        self.operation = operation
        self.show_details = False
        super().__init__()

        operation_type = operation.operation_type

        self.ope_title = QLabel(
            f"{operation.name} - {operation_type} ({operation.click_times} times)"
        )
        self.ope_title.setStyleSheet("font-weight: bold;")
        font = QFont()
        if operation.skip_this:
            font.setStrikeOut(True)
        self.ope_title.setFont(font)

        self.skip_btn = QPushButton("Skip")
        if operation.skip_this:
            self.skip_btn.setText("Unskip")
        self.skip_btn.setStyleSheet("padding: 4px;")
        self.skip_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.skip_btn.clicked.connect(self.handle_skip_changed)

        self.collapse_btn = QPushButton("Collapse Details")
        self.collapse_btn.setStyleSheet("padding: 4px;")
        self.collapse_btn.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.collapse_btn.clicked.connect(self.handle_collapsed)

        delete_btn = QPushButton("Delete Operation")
        delete_btn.setStyleSheet("padding: 4px; color: red;")
        delete_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        delete_btn.clicked.connect(self.delete_operation)

        title_hbox = QHBoxLayout()
        title_hbox.addWidget(self.ope_title)
        title_hbox.addWidget(self.skip_btn)
        title_hbox.addWidget(self.collapse_btn)
        title_hbox.addWidget(delete_btn)

        body_vbox = QVBoxLayout()
        if operation_type == OperationType.CLICK_IMG.value:
            body_vbox.addWidget(QLabel("Match Screen:"))
            body_vbox.addWidget(ImageWidget(operation.screen_img, self))

            body_vbox.addWidget(QLabel("Click:"))
            body_vbox.addWidget(ImageWidget(operation.click_img, self))

        elif operation_type == OperationType.CLICK_PERCENT.value:
            body_vbox.addWidget(
                ClickPercentImageWidget(
                    operation.screen_img,
                    operation.click_percent_x,
                    operation.click_percent_y,
                    self,
                )
            )
            body_vbox.addWidget(
                QLabel(
                    f"Click Percent: ({operation.click_percent_x}, {operation.click_percent_y})"
                )
            )
            if operation.click_percent_match_img:
                body_vbox.addWidget(QLabel("Match Screen:"))
                body_vbox.addWidget(
                    ImageWidget(operation.click_percent_match_img, self)
                )

        elif operation_type == OperationType.WAIT.value:
            if operation.is_implicity_wait:
                body_vbox.addWidget(QLabel("Implicit Wait:"))
                body_vbox.addWidget(QLabel(f"Wait: {operation.wait_timeout}s"))
            else:
                body_vbox.addWidget(
                    QLabel("Wait until GameScreen contains the following:")
                )
                body_vbox.addWidget(ImageWidget(operation.screen_img, self))
                body_vbox.addWidget(QLabel(f"Timeout: {operation.wait_timeout}s"))

        self.body_widget = QWidget()
        self.body_widget.setLayout(body_vbox)

        layout = QVBoxLayout()
        layout.addLayout(title_hbox)
        layout.addWidget(self.body_widget)
        self.setLayout(layout)

        self.collaspa_details()

    def handle_skip_changed(self):
        self.operation.skip_this = not self.operation.skip_this
        self.operation.save()
        if self.operation.skip_this:
            self.skip_btn.setText("Unskip")
            font = QFont()
            font.setStrikeOut(True)
            self.ope_title.setFont(font)
        else:
            self.skip_btn.setText("Skip")
            font = QFont()
            font.setStrikeOut(False)
            self.ope_title.setFont(font)

    def handle_collapsed(self):
        if self.show_details:
            self.collaspa_details()
        else:
            self.expand_details()

    def collaspa_details(self):
        self.show_details = False
        self.collapse_btn.setText("Expand Details")
        self.body_widget.hide()

    def expand_details(self):
        self.show_details = True
        self.collapse_btn.setText("Collapse Details")
        self.body_widget.show()

    def delete_operation(self):
        confirm = QMessageBox.question(
            self,
            "Delete Operation",
            f"Are you sure you want to delete this {self.operation.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.operation.delete_instance()
            self.deleteLater()


class TaskCardBody(QWidget):
    on_operations_order_changed = pyqtSignal(list)

    def __init__(self, task: Task):
        self.task = task
        super().__init__()

        self.draggable = DragWidget()
        self.draggable.on_order_change.connect(self.handle_order_changed)
        if len(self.task.operations) <= 0:
            item = QLabel("No Operations")
            item.reorder_data = None
            self.draggable.add_item(item)
        for op in task.get_orded_operations():
            item = OperationView(op)
            item.reorder_data = op
            item_container = DragItemContainer(item)
            self.draggable.add_item(item_container)

        layout = QVBoxLayout()
        layout.addWidget(self.draggable)
        self.setLayout(layout)

    def handle_order_changed(self, new_order):
        self.operation_order = [op.id for op in new_order]
        self.on_operations_order_changed.emit(new_order)

    def add_operation(self):
        self.task = Task.get_by_id(self.task.id)
        self.rerender_operations()

    def rerender_operations(self):
        layout = self.draggable.layout()
        clear_layout(layout)
        for op in self.task.get_orded_operations():
            item = OperationView(op)
            item.reorder_data = op
            drag_item_container = DragItemContainer(item)
            self.draggable.add_item(drag_item_container)


class TaskCard(QWidget):
    default_height = 100

    def __init__(self, task: Task):
        self.task = task
        self.min_h = self.default_height
        self.show_operations = False
        super().__init__()

        self.title_label = QLabel(self.task.name)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        font = QFont()
        if task.skip_this:
            font.setStrikeOut(True)
        self.title_label.setFont(font)

        self.skip_btn = QPushButton("Skip")
        if task.skip_this:
            self.skip_btn.setText("Unskip")
        self.skip_btn.setStyleSheet("padding: 4px;")
        self.skip_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.skip_btn.clicked.connect(self.handle_skip_changed)

        self.add_btn = QPushButton("Add Operation")
        self.add_btn.setStyleSheet("padding: 4px;")
        self.add_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.add_btn.clicked.connect(self.add_operation)

        self.collapse_btn = QPushButton("Collapse Operations")
        self.collapse_btn.setStyleSheet("padding: 4px;")
        self.collapse_btn.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.collapse_btn.clicked.connect(self.handle_collapsed)

        delete_btn = QPushButton("Delete Task")
        delete_btn.setStyleSheet("padding: 4px; color: red;")
        delete_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        delete_btn.clicked.connect(self.delete_task)

        title_box = QHBoxLayout()
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.skip_btn)
        title_box.addWidget(self.add_btn)
        title_box.addWidget(self.collapse_btn)
        title_box.addWidget(delete_btn)

        self.body_widget = TaskCardBody(self.task)
        self.body_widget.on_operations_order_changed.connect(
            self.handle_operations_order_changed
        )

        layout = QVBoxLayout()
        layout.addLayout(title_box)
        layout.addWidget(self.body_widget)
        self.setLayout(layout)

        self.collapse_operations()

    def handle_skip_changed(self):
        self.task.skip_this = not self.task.skip_this
        self.task.save()
        if self.task.skip_this:
            self.skip_btn.setText("Unskip")
            font = QFont()
            font.setStrikeOut(True)
            self.title_label.setFont(font)
        else:
            self.skip_btn.setText("Skip")
            font = QFont()
            font.setStrikeOut(False)
            self.title_label.setFont(font)

    def handle_operations_order_changed(self, new_order: list[Operation]):
        ids = [op.id for op in new_order]
        self.task.operation_order = ids
        self.task.save()

    def delete_task(self):
        confirm = QMessageBox.question(
            self,
            "Delete Task",
            f"Are you sure you want to delete {self.task.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.task.delete_instance()
            self.deleteLater()

    def handle_collapsed(self):
        if self.show_operations:
            self.collapse_operations()
        else:
            self.expand_operations()

    def collapse_operations(self):
        self.show_operations = False
        self.collapse_btn.setText("Expand Operations")
        self.body_widget.hide()

    def expand_operations(self):
        self.show_operations = True
        self.collapse_btn.setText("Collapse Operations")
        self.body_widget.show()

    def add_operation(self):
        self.screenshot_window = ScreenshotWidget()
        self.screenshot_window.on_screenshot_captured.connect(
            self.open_operation_editor
        )
        self.screenshot_window.show()

    def open_operation_editor(self, screenshot: QPixmap):
        self.operation_editor = OperationEditor(self.task, screenshot)
        self.operation_editor.on_operation_saved.connect(self.handle_operation_saved)
        self.operation_editor.show()

    def handle_operation_saved(self, operation: Operation):
        self.body_widget.add_operation()
        self.task = Task.get_by_id(self.task.id)
