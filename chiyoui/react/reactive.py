from PyQt6.QtWidgets import QWidget
from uuid import uuid4

from ..layout import VBox, HBox, ScrollArea
from ..widget import Button, Label


class VirtualNode:
    def __init__(self, *args, tag, key=None, **kwargs):
        self.tag: str = tag
        self.key: str = key or str(uuid4())
        self.children: list[VirtualNode] = args
        self.props: dict = kwargs

    def __repr__(self):
        return f"<VirtualNode tag={self.tag} key={self.key} props={self.props} children={self.children}>"

    def to_reactive(
        self,
        *,
        parent=None,
        child=None,
        sibling=None,
    ):
        widget = None
        if self.tag == "vbox":
            widget = VBox(**self.props)
            widget.setObjectName(self.key)
        elif self.tag == "hbox":
            widget = HBox(**self.props)
            widget.setObjectName(self.key)
        elif self.tag == "scrollarea":
            widget = ScrollArea(**self.props)
            widget.setObjectName(self.key)
        elif self.tag == "button":
            widget = Button(**self.props)
            widget.setObjectName(self.key)
        elif self.tag == "label":
            widget = Label(**self.props)
            widget.setObjectName(self.key)
        else:
            raise ValueError(f"Invalid tag: {self.tag}")

        return ReactiveNode(
            *self.children,
            tag=self.tag,
            key=self.key,
            widget=widget,
            parent=parent,
            child=child,
            sibling=sibling,
        )

    def to_reactive_tree(self):
        root = self.to_reactive()
        stack = [root]

        while len(stack) > 0:
            current = stack.pop()
            if len(current.children) > 0:
                prevSibling = None
                for idx, child in enumerate(current.children):
                    child_reactive = child.to_reactive(parent=current)
                    if idx == 0:
                        current.child = child_reactive
                    elif prevSibling:
                        prevSibling.sibling = child_reactive
                    prevSibling = child_reactive
                    stack.append(child_reactive)

        return root


class ReactiveNode:
    def __init__(
        self,
        *args,
        tag,
        key=None,
        widget=None,
        parent=None,
        child=None,
        sibling=None,
        **kwargs,
    ):
        self.tag: str = tag
        self.key: str = key
        self.widget: QWidget = widget
        self.parent: ReactiveNode = parent
        self.child: ReactiveNode = child
        self.sibling: ReactiveNode = sibling
        self.children: list[VirtualNode] = args
        self.props: dict = kwargs

    def __repr__(self):
        return f"<ReactiveNode tag={self.tag} key={self.key} widget={self.widget}>"

    def print_tree(self):
        stack = [[0, self]]
        while len(stack) > 0:
            level, current = stack.pop()
            print("  " * level, current)
            if current.child:
                stack.append([level + 1, current.child])
            if current.sibling:
                stack.append([level, current.sibling])

    def for_each(self, cb):
        stack = [self]
        while len(stack) > 0:
            current = stack.pop()
            cb(current)
            if current.child:
                stack.append(current.child)
            if current.sibling:
                stack.append(current.sibling)


class Reactive:
    def __init__(self, container: QWidget, node: VirtualNode):
        self.container = container
        self.root = node.to_reactive_tree()

    def render(self):
        self.commit()
        self.container.layout().addWidget(self.root.widget)

    def commit(self):
        self.root.for_each(lambda node: self.commit_node(node))

    def commit_node(self, node: ReactiveNode):
        if node.parent:
            node.parent.widget.layout().addWidget(node.widget)
