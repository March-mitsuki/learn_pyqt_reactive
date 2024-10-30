from loguru import logger
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from PyQt6.QtCore import Qt

from .utils import apply_style_kwargs, add_widget_to_layout, handle_signal


class ChiyoUiWidget(QWidget):
    """
    use `self.layout()` to access the layout
    """

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

        self.chiyo_children = []
        for widget in args:
            add_widget_to_layout(layout, widget)
        apply_style_kwargs(self, layout, **kwargs)

        if kwargs.get("ref", None):
            kwargs["ref"].current = self

        self.setLayout(layout)


class HBox(ChiyoUiWidget):
    """
    use `self.layout()` to access the layout
    """

    _name = "hbox"

    def __init__(self, *args, **kwargs):
        logger.debug("HBox init with args: '{}' and kwargs: '{}'", args, kwargs)

        kwargs["layout"] = kwargs.get("layout", QHBoxLayout())
        kwargs["spacing"] = kwargs.get("spacing", 0)
        kwargs["margin"] = kwargs.get("margin", (0, 0, 0, 0))
        kwargs["alignment"] = kwargs.get("alignment", Qt.AlignmentFlag.AlignLeft)
        super().__init__(*args, **kwargs)


class VBox(ChiyoUiWidget):
    """
    use `self.layout()` to access the layout
    """

    _name = "vbox"

    def __init__(self, *args, **kwargs):
        logger.debug("VBox init with args: '{}' and kwargs: '{}'", args, kwargs)

        kwargs["alignment"] = kwargs.get("alignment", Qt.AlignmentFlag.AlignTop)
        kwargs["spacing"] = kwargs.get("spacing", 0)
        kwargs["margin"] = kwargs.get("margin", (0, 0, 0, 0))
        kwargs["layout"] = kwargs.get("layout", QVBoxLayout())
        super().__init__(*args, **kwargs)


class ScrollArea(ChiyoUiWidget):
    """
    use `self.layout()` to access the layout

    use `self.scroll_area` to access the scroll area

    Default layout is QVBoxLayout, you can change it by passing `layout` argument
    """

    _name = "scroll_area"

    def __init__(self, *args, **kwargs):
        logger.debug(
            "ScrollArea init with args: '{}' and kwargs: '{}'",
            args,
            kwargs,
        )

        widget_resizable = kwargs.pop("widget_resizable", True)
        super().__init__(*args, **kwargs)

        self.scroll_area = QScrollArea()
        handle_signal(
            widget_resizable, lambda x: self.scroll_area.setWidgetResizable(x)
        )
        self.layout().addWidget(self.scroll_area)
