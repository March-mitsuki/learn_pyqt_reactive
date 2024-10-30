from PyQt6.QtWidgets import QWidget

from .reactive import VirtualNode, Reactive


class ReactiveButton(VirtualNode):
    def __init__(self, *args, text, **kwargs):
        super().__init__(tag="button", text=text, *args, **kwargs)


class ReactiveVBox(VirtualNode):
    def __init__(self, *args, **kwargs):
        super().__init__(tag="vbox", *args, **kwargs)


def render(container: QWidget, node: VirtualNode):
    Reactive(container, node).render()
