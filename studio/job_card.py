from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QInputDialog,
    QMessageBox,
)
from PyQt6.QtCore import QThreadPool

from db.models import Job, Task
from .task_card import TaskCard
from .dnd_widget import DragItemContainer, DragWidget
from .utils import clear_layout
from .excution import JobExcution


class JobCard(QWidget):
    def __init__(self, job: Job):
        self.job = job
        self.show_tasks = False
        super().__init__()

        self.title_label = QLabel(job.name)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.title_label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        self.window_name_label = QLabel(f" - ({job.window_name})")
        self.window_name_label.setStyleSheet("font-size: 20px;")

        self.run_btn = QPushButton("Run Job")
        self.run_btn.setStyleSheet("padding: 8px; color: blue;")
        self.run_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.run_btn.clicked.connect(self.run_job)

        self.add_task_btn = QPushButton("Add Task")
        self.add_task_btn.setStyleSheet("padding: 8px;")
        self.add_task_btn.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.add_task_btn.clicked.connect(self.add_task)

        self.collapse_btn = QPushButton("Collapse Tasks")
        self.collapse_btn.setStyleSheet("padding: 8px;")
        self.collapse_btn.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.collapse_btn.clicked.connect(self.handle_collapsed)

        delete_btn = QPushButton("Delete Job")
        delete_btn.setStyleSheet("padding: 8px; color: red;")
        delete_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        delete_btn.clicked.connect(self.delete_job)

        title_box = QHBoxLayout()
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.window_name_label)
        title_box.addWidget(self.run_btn)
        title_box.addWidget(self.add_task_btn)
        title_box.addWidget(self.collapse_btn)
        title_box.addWidget(delete_btn)

        self.body_widget = DragWidget()
        self.body_widget.on_order_change.connect(self.handle_order_changed)
        if len(self.job.tasks) <= 0:
            item = QLabel("No Tasks")
            item.reorder_data = None
            self.body_widget.add_item(item)
        for task in self.job.get_orded_tasks():
            item = TaskCard(task)
            item.reorder_data = task
            drag_item_container = DragItemContainer(item)
            self.body_widget.add_item(drag_item_container)

        layout = QVBoxLayout()
        layout.addLayout(title_box)
        layout.addWidget(self.body_widget)
        self.setLayout(layout)

        self.collapse_tasks()

    def run_job(self):
        worker = JobExcution(self.job)
        worker.signals.finished.connect(
            lambda: QMessageBox.information(
                self, "Job Finished", "Job Finished Successfully"
            )
        )
        worker.signals.error.connect(
            lambda err: QMessageBox.critical(self, "Error", str(err))
        )
        QThreadPool.globalInstance().start(worker)

    def add_task(self):
        name, ok = QInputDialog.getText(self, "Create Task", "Task Name:")
        if ok and name:
            Task.create(name=name, job=self.job)
            self.handle_data_changed()

    def handle_order_changed(self, order):
        ids = [item.id for item in order]
        self.job.task_order = ids
        self.job.save()

    def handle_data_changed(self):
        """按理来说应该是计算哪个加哪个减了, 图方便先直接全部重载"""
        self.job = Job.get_by_id(self.job.id)
        self.rerender_tasks()

    def rerender_tasks(self):
        layout = self.body_widget.layout()
        clear_layout(layout)
        if len(self.job.tasks) <= 0:
            item = QLabel("No Tasks")
            item.reorder_data = None
            self.body_widget.add_item()
        for task in self.job.get_orded_tasks():
            item = TaskCard(task)
            item.reorder_data = task
            drag_item_container = DragItemContainer(item)
            self.body_widget.add_item(drag_item_container)

    def handle_collapsed(self):
        if self.show_tasks:
            self.collapse_tasks()
        else:
            self.expand_tasks()

    def collapse_tasks(self):
        self.show_tasks = False
        self.collapse_btn.setText("Expand Tasks")
        self.body_widget.hide()

    def expand_tasks(self):
        self.show_tasks = True
        self.collapse_btn.setText("Collapse Tasks")
        self.body_widget.show()

    def delete_job(self):
        confirm = QMessageBox.question(
            self,
            "Delete Job",
            f"Are you sure you want to delete {self.job.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.job.delete_instance()
            self.deleteLater()
