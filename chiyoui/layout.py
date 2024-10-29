from loguru import logger
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

from .utils import apply_style_kwargs, add_widget_to_layout


class ChiyoUiWidget(QWidget):
    _name = "chiyo_ui_widget"

    def __init__(self, *args, **kwargs):
        logger.debug(
            "ChiyoUiWidget init with args: '{}' and kwargs: '{}'",
            args,
            kwargs,
        )

        super().__init__()

        defult_layout = QVBoxLayout()
        defult_layout.setContentsMargins(0, 0, 0, 0)
        defult_layout.setSpacing(0)
        layout = kwargs.pop("layout", defult_layout)
        for widget in args:
            add_widget_to_layout(layout, widget)
        apply_style_kwargs(self, layout, **kwargs)

        if kwargs.get("ref", None):
            kwargs["ref"].current = self

        self.setLayout(layout)


class HBox(ChiyoUiWidget):
    _name = "hbox"

    def __init__(self, *args, **kwargs):
        logger.debug("HBox init with args: '{}' and kwargs: '{}'", args, kwargs)

        kwargs["layout"] = kwargs.get("layout", QHBoxLayout())
        kwargs["spacing"] = kwargs.get("spacing", 0)
        kwargs["margin"] = kwargs.get("margin", (0, 0, 0, 0))
        kwargs["alignment"] = kwargs.get("alignment", Qt.AlignmentFlag.AlignLeft)
        super().__init__(*args, **kwargs)


class VBox(ChiyoUiWidget):
    _name = "vbox"

    def __init__(self, *args, **kwargs):
        logger.debug("VBox init with args: '{}' and kwargs: '{}'", args, kwargs)

        kwargs["alignment"] = kwargs.get("alignment", Qt.AlignmentFlag.AlignTop)
        kwargs["spacing"] = kwargs.get("spacing", 0)
        kwargs["margin"] = kwargs.get("margin", (0, 0, 0, 0))
        kwargs["layout"] = kwargs.get("layout", QVBoxLayout())
        super().__init__(*args, **kwargs)
