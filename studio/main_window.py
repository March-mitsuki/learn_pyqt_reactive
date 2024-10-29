from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
)


from db.models import Job
from .job_card import JobCard
from .utils import zoom_rect, clear_layout
from .multi_input_dialog import MultiInputDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Auto GUI Studio")
        scrreen_geom = QApplication.primaryScreen().geometry()
        self.setGeometry(zoom_rect(scrreen_geom, 0.5))

        self.create_task_btn = QPushButton("Create Job", self)
        self.create_task_btn.clicked.connect(self.create_job)

        self.exit_button = QPushButton("退出", self)
        self.exit_button.clicked.connect(QApplication.quit)

        # 左侧内容
        self.left_content = QVBoxLayout()
        self.left_content.addWidget(self.create_task_btn)
        self.left_content.addWidget(self.exit_button)

        # 右侧内容
        self.right_content = QVBoxLayout()
        all_jobs = Job.select()
        if len(all_jobs) <= 0:
            self.right_content.addWidget(QLabel("No Jobs"))
        for job in all_jobs:
            self.right_content.addWidget(JobCard(job))

        right_container = QWidget()
        right_container.setLayout(self.right_content)

        right_scroll_area = QScrollArea()
        right_scroll_area.setWidgetResizable(True)
        right_scroll_area.setWidget(right_container)

        hbox = QHBoxLayout()
        hbox.addLayout(self.left_content)
        hbox.addWidget(right_scroll_area)

        container = QWidget()
        container.setLayout(hbox)
        self.setCentralWidget(container)

    def create_job(self):
        input_dialog = MultiInputDialog("Create Job", ["Name:", "Window Name:"])
        input_dialog.exec()
        values, ok = input_dialog.get_values()
        if ok:
            name, window_name = values
            Job.create(name=name, window_name=window_name)
            self.rerender_jobs()

    def rerender_jobs(self):
        all_jobs = Job.select()
        clear_layout(self.right_content)
        if len(all_jobs) <= 0:
            self.right_content.addWidget(QLabel("No Jobs"))
        for job in all_jobs:
            self.right_content.addWidget(JobCard(job))
