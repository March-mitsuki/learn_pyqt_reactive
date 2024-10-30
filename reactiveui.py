import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

from studio.utils import zoom_rect
from chiyoui.react.widget import ReactiveButton, ReactiveVBox, render
from chiyoui.reactive import use_signal

# for test
import threading


def set_timeout(func, sec):
    timer = threading.Timer(sec, func)
    timer.start()


class ReactiveUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ReactiveUI")
        scrreen_geom = QApplication.primaryScreen().geometry()
        self.setGeometry(zoom_rect(scrreen_geom, 0.5))

        self.root = QWidget()
        self.root.setLayout(QVBoxLayout())
        self.setCentralWidget(self.root)

        reactive_text = use_signal("Reactive!")
        set_timeout(lambda: reactive_text.set("Changed!"), 3)
        set_timeout(lambda: reactive_text.set("Changed 2!"), 6)
        reactive_bg = use_signal("background-color: red;")
        set_timeout(lambda: reactive_bg.set("background-color: blue;"), 3)
        set_timeout(lambda: reactive_bg.set("background-color: green;"), 6)

        self.app = ReactiveVBox(
            ReactiveButton(text=reactive_text, qss=reactive_bg),
            ReactiveButton(text="退出"),
            ReactiveVBox(
                ReactiveButton(text="Create Job - 2"),
                ReactiveButton(text="退出 - 2"),
            ),
            ReactiveButton(text="Create Job - 3"),
        )

        render(self.root, self.app)

    def submit(self, values):
        print("Submitted", values)

    def handle_validate_error(self, errors):
        print("Validation errors", errors)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ReactiveUI()
    window.show()

    sys.exit(app.exec())
