from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget
from uuid import uuid4

from .widget import VBox, Button, Label

__current_listener__ = None


class Signal:
    def __init__(self, init_value):
        super().__init__()
        self._value = init_value
        self._subscribers = set()

    def get(self):
        if __current_listener__:
            self._subscribers.add(__current_listener__)
        return self._value

    def set(self, next_value):
        if callable(next_value):
            raise NotImplementedError("Callable not supported yet")
        if self._value == next_value:
            return
        self._value = next_value
        for subscriber in self._subscribers:
            subscriber()

    def subscribe(self, cb):
        self._subscribers.add(cb)


def create_effect(cb):
    global __current_listener__
    prev_listener = __current_listener__
    __current_listener__ = cb
    cb()
    __current_listener__ = prev_listener


def create_signal(value):
    s = Signal(value)
    return (s.get, s.set)


def create_memo(cb):
    value, set_value = create_signal(None)
    create_effect(lambda: set_value(cb()))
    return value


class VirtualWidget:
    def __init__(self, *args, tag, key=None, **kwargs):
        self.tag: str = tag
        self.key: str = key or str(uuid4())
        self.children: list[VirtualWidget] = args
        self.props: dict = kwargs
        # self.children: list[VirtualWidget] = Signal(args)
        # self.props: dict = Signal(kwargs)

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
        elif self.tag == "button":
            widget = Button(**self.props)
        elif self.tag == "label":
            widget = Label(**self.props)
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
            **self.props,
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
        self.children: list[VirtualWidget] = args
        self.props: dict = kwargs

    def __repr__(self):
        return f"<ReactiveNode tag={self.tag} key={self.key} widget={self.widget}>"

    def for_each(self, cb):
        stack = [[0, self]]
        while len(stack) > 0:
            depth, current = stack.pop()
            cb(current, depth)
            if current.child:
                stack.append([depth + 1, current.child])
            if current.sibling:
                stack.append([depth, current.sibling])

    def print_tree(self):
        self.for_each(lambda depth, current: print("  " * depth, current))


class Component(ABC):
    @abstractmethod
    def render(self, *args, **kwargs) -> VirtualWidget:
        raise NotImplementedError()


class Reactive:
    def __init__(self, container: QWidget, node: Component):
        self.container = container
        self.root = node.render().to_reactive_tree()

    def render(self):
        self.commit()
        self.container.layout().addWidget(self.root.widget)

    def commit(self):
        self.root.for_each(lambda node, _: self.commit_node(node))

    def commit_node(self, node: ReactiveNode):
        if node.parent:
            node.parent.widget.layout().addWidget(node.widget)


def render(container: QWidget, comp: Component):
    Reactive(container, comp).render()
