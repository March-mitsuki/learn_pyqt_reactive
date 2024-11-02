import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

from studio.utils import zoom_rect
from reactpyqt.component import Button, VBox, Label
from reactpyqt.core import Component, render, use_state


# for test
import threading


def set_timeout(func, sec):
    timer = threading.Timer(sec, func)
    timer.start()


class App(Component):
    def render(self):
        # text, set_text = use_state("Welcome to ReactivePyQt")
        # set_timeout(lambda: set_text("Hello World"), 3)

        self.app = VBox(
            Label(text="Welcome to ReactivePyQt", key="label"),
            Button(text="Home", key="home"),
            Button(text="退出", key="exit"),
            VBox(
                Button(text="Create Job - 2", key="btn_in_vbox_1"),
                Button(text="退出 - 2", key="btn_in_vbox_2"),
                key="vbox",
            ),
            Button(text="Create Job - 3", key="btn_after_vbox"),
            key="wrapper",
        )
        return self.app


class ReactiveUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ReactiveUI")
        scrreen_geom = QApplication.primaryScreen().geometry()
        self.setGeometry(zoom_rect(scrreen_geom, 0.5))

        self.root = QWidget()
        self.root.setLayout(QVBoxLayout())
        self.setCentralWidget(self.root)

        render(self.root, App())

    def submit(self, values):
        print("Submitted", values)

    def handle_validate_error(self, errors):
        print("Validation errors", errors)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ReactiveUI()
    window.show()

    sys.exit(app.exec())
