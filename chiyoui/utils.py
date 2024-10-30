from PyQt6.QtWidgets import QWidget, QLayout, QLabel

from .reactive import Signal


def handle_signal(value, set_func):
    if isinstance(value, Signal) and callable(set_func):
        set_func(value.current())
        value.on_change.connect(set_func)
    else:
        set_func(value)


def apply_style_kwargs(widget: QWidget, layout: QLayout, **kwargs):
    for key, value in kwargs.items():
        if key == "margin":
            # layout.setContentsMargins(*value)
            handle_signal(value, lambda v: layout.setContentsMargins(*v))
        elif key == "spacing":
            # layout.setSpacing(value)
            handle_signal(value, lambda v: layout.setSpacing(v))
        elif key == "alignment":
            # layout.setAlignment(value)
            handle_signal(value, lambda v: layout.setAlignment(v))
        elif key == "size_policy":
            # layout.setSizeConstraint(value)
            handle_signal(value, lambda v: layout.setSizeConstraint(v))
        elif key == "alignment":
            # layout.setAlignment(value)
            handle_signal(value, lambda v: layout.setAlignment(v))
        elif key == "qss":
            # widget.setStyleSheet(value)
            handle_signal(value, lambda v: widget.setStyleSheet(v))
        elif key == "minimum_size":
            # widget.setMinimumSize(*value)
            handle_signal(value, lambda v: widget.setMinimumSize(*v))
        elif key == "maximum_size":
            # widget.setMaximumSize(*value)
            handle_signal(value, lambda v: widget.setMaximumSize(*v))
        elif key == "size":
            # widget.setFixedSize(*value)
            handle_signal(value, lambda v: widget.setFixedSize(*v))


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
