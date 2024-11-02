from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLayout,
    QLabel,
    QPushButton,
)
from PyQt6.QtCore import Qt


def apply_style_kwargs(widget: QWidget, layout: QLayout, **kwargs):
    for key, value in kwargs.items():
        if key == "margin":
            layout.setContentsMargins(*value)
        elif key == "spacing":
            layout.setSpacing(value)
        elif key == "alignment":
            layout.setAlignment(value)
        elif key == "size_policy":
            layout.setSizeConstraint(value)
        elif key == "alignment":
            layout.setAlignment(value)
        elif key == "qss":
            widget.setStyleSheet(value)
        elif key == "minimum_size":
            widget.setMinimumSize(*value)
        elif key == "maximum_size":
            widget.setMaximumSize(*value)
        elif key == "size":
            widget.setFixedSize(*value)


def add_widget_to_layout(layout: QLayout, widget: QWidget | str | int):
    layout.addWidget(create_widget(widget))


def create_widget(widget: QWidget | str | int):
    if isinstance(widget, QWidget):
        return widget
    elif isinstance(widget, str):
        return QLabel(widget)
    elif isinstance(widget, (int, float)):
        return QLabel(str(widget))
    else:
        raise TypeError(f"Invalid widget: {widget}")


class Widget(QWidget):
    """
    A QWidget wrapper.
    """

    def __init__(self, *args, **kwargs):
        super().__init__()

        defult_layout = QVBoxLayout()
        defult_layout.setContentsMargins(0, 0, 0, 0)
        defult_layout.setSpacing(0)
        layout = kwargs.pop("layout", defult_layout)

        self.chiyo_children = []
        for widget in args:
            add_widget_to_layout(layout, widget)
        apply_style_kwargs(self, layout, **kwargs)

        if kwargs.get("ref", None):
            kwargs["ref"] = self
        if kwargs.get("key", None):
            self.setObjectName(kwargs["key"])

        self.setLayout(layout)


class VBox(Widget):
    """
    A vertical box layout.
    """

    def __init__(self, *args, **kwargs):
        kwargs["layout"] = QVBoxLayout()
        kwargs["spacing"] = kwargs.get("spacing", 0)
        kwargs["margin"] = kwargs.get("margin", (0, 0, 0, 0))
        kwargs["alignment"] = kwargs.get("alignment", Qt.AlignmentFlag.AlignLeft)
        super().__init__(*args, **kwargs)


class HBox(Widget):
    """
    A horizontal box layout.
    """

    def __init__(self, *args, **kwargs):
        kwargs["layout"] = QHBoxLayout()
        kwargs["spacing"] = kwargs.get("spacing", 0)
        kwargs["margin"] = kwargs.get("margin", (0, 0, 0, 0))
        kwargs["alignment"] = kwargs.get("alignment", Qt.AlignmentFlag.AlignLeft)
        super().__init__(*args, **kwargs)


class Button(Widget):
    """
    A button widget.
    """

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)

        self.button = QPushButton(text=text)
        self.button.clicked.connect(self.clicked)
        self.layout().addWidget(self.button)

    def clicked(self):
        print("Button clicked")


class Label(Widget):
    """
    A label widget.
    """

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)

        self.label = QLabel(text=text)
        self.layout().addWidget(self.label)
