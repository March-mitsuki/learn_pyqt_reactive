import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from marshmallow import Schema, fields, validate, ValidationError

from studio.utils import zoom_rect
from chiyoui.widget import Button, Label
from chiyoui.layout import VBox, HBox
from chiyoui.form_controls import Input, Select, Form, NumberInput
from chiyoui.inspector import InspectorDialog
from chiyoui import DEFAULT_GLOBAL_QSS
from chiyoui.reactive import use_ref, use_signal

# for test
import threading


def set_timeout(func, sec):
    timer = threading.Timer(sec, func)
    timer.start()


def validate_age(value):
    if value < 18:
        raise ValidationError("未成年人不可注册")


class FormSchema(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=5),
    )
    country = fields.String(required=True)
    age = fields.Integer(
        required=True,
        validate=[validate_age, validate.Range(min=0)],
    )


class ChiyoUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ChiyoUI")
        scrreen_geom = QApplication.primaryScreen().geometry()
        self.setGeometry(zoom_rect(scrreen_geom, 0.5))
        self.setStyleSheet(DEFAULT_GLOBAL_QSS.to_str())

        home_btn_ref = use_ref()
        reactive_text = use_signal("Reactive!")
        set_timeout(lambda: reactive_text.set("Changed!"), 3)
        set_timeout(lambda: reactive_text.set("Changed 2!"), 6)

        reactive_bg = use_signal("background-color: red;")
        set_timeout(lambda: reactive_bg.set("background-color: blue;"), 3)
        set_timeout(lambda: reactive_bg.set("background-color: green;"), 6)

        self.main = HBox(
            VBox(
                "Welcome to ChiyoUI",
                Label(text=reactive_text, qss=reactive_bg),
                Button(text="Home", ref=home_btn_ref),
                Button(text="About"),
                Button(
                    text="Test",
                    on_click=lambda: print("Test", home_btn_ref.current.button.text()),
                ),
            ),
            VBox(
                Form(
                    Input(
                        label="Name",
                        form_field="name",
                        placeholder="Enter your name",
                    ),
                    Select(
                        label="Country",
                        form_field="country",
                        options=[
                            ("America", "america"),
                            ("中国", "china"),
                            ("日本", "japan"),
                        ],
                    ),
                    NumberInput(
                        label="Age",
                        form_field="age",
                        placeholder="Enter your age",
                    ),
                    Button(text="Submit", type="submit"),
                    on_submit=self.submit,
                    validation_schema=FormSchema(),
                    on_validate_error=self.handle_validate_error,
                ),
                margin=(0, 0, 0, 0),
                spacing=0,
                alignment=Qt.AlignmentFlag.AlignTop,
            ),
        )
        self.inspector = InspectorDialog(self)
        self.inspector.show()

        self.setCentralWidget(self.main)

    def submit(self, values):
        print("Submitted", values)

    def handle_validate_error(self, errors):
        print("Validation errors", errors)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ChiyoUI()
    window.show()

    sys.exit(app.exec())
