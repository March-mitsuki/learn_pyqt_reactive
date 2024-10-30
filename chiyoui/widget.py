from loguru import logger
from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal

from .layout import ChiyoUiWidget
from .reactive import Signal


class Label(ChiyoUiWidget):
    _name = "label"

    def __init__(self, *args, text: str | Signal, **kwargs):
        logger.debug(
            "Label init with text: '{}' and args: '{}' and kwargs: '{}'",
            text,
            args,
            kwargs,
        )

        super().__init__(*args, **kwargs)

        if isinstance(text, Signal):
            self.label = QLabel(text.current())
            text.on_change.connect(self.label.setText)
        else:
            self.label = QLabel(text)
        self.layout().addWidget(self.label)


class Button(ChiyoUiWidget):
    """
    use `self.button` to access the button
    """

    _name = "button"
    _on_click = pyqtSignal()

    def __init__(
        self,
        *args,
        text: str,
        on_click=None,
        type="normal",
        **kwargs,
    ):
        logger.debug(
            "Button init with text: '{}' and args: '{}' and kwargs: '{}'",
            text,
            args,
            kwargs,
        )

        super().__init__(*args, **kwargs)
        self.type = type

        if isinstance(text, Signal):
            self.button = QPushButton(text.current())
            text.on_change.connect(self.button.setText)
        else:
            self.button = QPushButton(text)
        self.button.clicked.connect(on_click or self._on_click.emit)
        self.layout().addWidget(self.button)

    def reconnect(self, on_click):
        self.button.clicked.disconnect()
        self.button.clicked.connect(on_click or self._on_click.emit)
