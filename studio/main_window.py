from PyQt6.QtWidgets import QApplication, QMainWindow

from chiyoui.layout import VBox, HBox, ScrollArea
from chiyoui.widget import Button, Label
from chiyoui.reactive import use_signal

from db.models import Job
from .job_card import JobCard
from .utils import zoom_rect
from .multi_input_dialog import MultiInputDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Auto GUI Studio")
        scrreen_geom = QApplication.primaryScreen().geometry()
        self.setGeometry(zoom_rect(scrreen_geom, 0.5))

        self.job_widgets = use_signal([])

        all_jobs = Job.select()
        if len(all_jobs) <= 0:
            self.job_widgets.set([Label("No Jobs")])
        for job in all_jobs:
            self.job_widgets.set(lambda prev: prev.append(JobCard(job)))

        self.main = HBox(
            VBox(
                "Welcome to Auto GUI Studio",
                Button(text="Create Job", on_click=self.create_job),
                Button(text="退出", on_click=QApplication.quit),
            ),
            ScrollArea(
                self.job_widgets,
            ),
        )

        self.setCentralWidget(self.main)

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
        self.job_widgets.set([])
        if len(all_jobs) <= 0:
            self.job_widgets.set([Label("No Jobs")])
        for job in all_jobs:
            self.job_widgets.set(lambda prev: prev.append(JobCard(job)))
