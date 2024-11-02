from .core import VirtualWidget


class VBox(VirtualWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(tag="vbox", *args, **kwargs)


class Button(VirtualWidget):
    def __init__(self, text, **kwargs):
        super().__init__(tag="button", **kwargs)
        self.props["text"] = text


class Label(VirtualWidget):
    def __init__(self, text, **kwargs):
        super().__init__(tag="label", **kwargs)
        self.props["text"] = text
