from __future__ import annotations
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget
from uuid import uuid4
from enum import IntFlag

from .widget import VBox, Button, Label


class EventEmitter:
    def __init__(self):
        self._events = {}

    def on(self, event, listener):
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(listener)

    def emit(self, event, *args, **kwargs):
        if event in self._events:
            for listener in self._events[event]:
                listener(*args, **kwargs)

    def off(self, event, listener=None):
        if event in self._events:
            if listener:
                self._events[event] = [
                    el for el in self._events[event] if el != listener
                ]
            else:
                del self._events[event]


wip_node = None
is_init_render = True
rerender_signal = EventEmitter()


class Operation(IntFlag):
    """A 16-bit flag to represent the operation type."""

    # fmt: off
    NONE =     0b0000000000000000
    UPDATE =   0b0000000000000001
    INSERT =   0b0000000000000010
    DELETE =   0b0000000000000100
    REPLACE =  0b0000000000001000
    # fmt: on


def use_state(initial_state):
    value = initial_state

    def setter(next_state):
        global is_init_render
        if is_init_render:
            return
        nonlocal value
        if value == next_state:
            return
        global wip_node
        value = next_state
        wip_node.effect_tag = Operation.UPDATE

    return value, setter


def create_qt_widget(tag, **props):
    widget = None
    if tag == "vbox":
        widget = VBox(**props)
    elif tag == "button":
        widget = Button(**props)
    elif tag == "label":
        widget = Label(**props)
    else:
        raise ValueError(f"Invalid tag: {tag}")
    return widget


def reconcile_children(v_wgt):
    """
    Parameters:
    - v_wgt: VirtualWidget
    """
    root = v_wgt.to_reactive()
    stack = [(root, v_wgt.children)]

    while len(stack) > 0:
        current, children = stack.pop()
        # if len(children) > 0:
        prevSibling = None
        for idx, child in enumerate(children):
            child_reactive = child.to_reactive(parent=current)
            if idx == 0:
                current.child = child_reactive
            elif prevSibling:
                prevSibling.sibling = child_reactive
            prevSibling = child_reactive
            stack.append((child_reactive, child.children))

    return root


def perform_unit_work(node):
    """
    Parameters:
    - node: ReactiveNode
    """
    global wip_node
    wip_node = node
    if not node.parent:
        return

    if node.effect_tag & Operation.UPDATE:
        node.widget = create_qt_widget(node.tag, **node.props)
        node.effect_tag = None


class VirtualWidget:
    def __init__(self, *args, tag, key=None, **kwargs):
        self.tag: str = tag
        self.key: str = key or str(uuid4())
        self.children: list[VirtualWidget] = args
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
        return ReactiveNode(
            tag=self.tag,
            key=self.key,
            parent=parent,
            child=child,
            sibling=sibling,
            **self.props,
        )

    def to_reactive_tree(self):
        root = self.to_reactive()
        stack = [(root, self.children)]

        while len(stack) > 0:
            current, children = stack.pop()
            prevSibling = None
            for idx, child in enumerate(children):
                child_reactive = child.to_reactive(parent=current)
                if idx == 0:
                    current.child = child_reactive
                elif prevSibling:
                    prevSibling.sibling = child_reactive
                prevSibling = child_reactive
                stack.append((child_reactive, child.children))

        return root


class ReactiveNode:
    def __init__(
        self,
        *,
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
        # self.children: list[VirtualWidget] = args
        self.props: dict = kwargs
        self.hooks = list()
        self.effect_tag = Operation.NONE

    def __repr__(self):
        return f"<ReactiveNode tag={self.tag} key={self.key} widget={self.widget}>"

    def for_each(self, *, on_enter, on_exit=None, when_end=None):
        if not callable(on_enter):
            raise ValueError("for_each cb must be callable")
        stack = [(0, False, self)]
        while len(stack) > 0:
            depth, visited, current = stack.pop()
            if not visited:
                on_enter(current, depth)
                stack.append((depth, True, current))
                if current.child:
                    stack.append((depth + 1, False, current.child))
                if current.sibling:
                    stack.append((depth, False, current.sibling))
            elif callable(on_exit):
                on_exit(current, depth)
        if callable(when_end):
            when_end()

    def print_tree(self):
        self.for_each(on_enter=lambda current, depth: print("  " * depth, current))

    def debug(self):
        self.for_each(
            on_enter=lambda current, _: print(
                "on_enter",
                current.key,
                "parent",
                current.parent.key if current.parent else None,
            ),
            on_exit=lambda current, _: print(
                "on_exit",
                current.key,
                "parent",
                current.parent.key if current.parent else None,
            ),
        )


class Component(ABC):
    @abstractmethod
    def render(self, *args, **kwargs) -> VirtualWidget | Component:
        raise NotImplementedError()


class Reactive:
    def __init__(self, container: QWidget, node: Component):
        self.container = container
        self.root = node

    def render(self):
        self.container.layout().addWidget(self.root.render().to_reactive().widget)
        self.start_work(self.root)

    def start_work(self, node: Component):
        rendered = node.render()
        # stack = [rendered]
        # while len(stack) > 0:
        #     current = stack.pop()
        #     if isinstance(current, Component):
        #         self.commit_component(current)
        #     elif isinstance(current, VirtualWidget):
        #         current.to_reactive_tree().for_each(
        #             on_enter=self.commit_node,
        #         )
        #     else:
        #         raise ValueError("Invalid return type")

        if isinstance(rendered, Component):
            self.start_work(rendered)
        elif isinstance(rendered, VirtualWidget):
            rendered.to_reactive_tree().for_each(
                on_enter=self.commit_node,
            )
        else:
            raise ValueError("Invalid return type")

    def process_node(self, node: ReactiveNode, depth: int):
        global wip_node
        wip_node = node
        if not node.parent:
            return

    def commit_node(self, node: ReactiveNode, depth: int):
        global wip_node
        wip_node = node

        if not node.parent:
            return

        global is_init_render
        if is_init_render:
            node.parent.widget.layout().addWidget(node.widget)
            return

        if node.effect_tag & Operation.UPDATE:
            node.widget = create_qt_widget(node.tag, **node.props)
            node.effect_tag = None


def render(container: QWidget, comp: Component):
    Reactive(container, comp).render()
    global is_init_render
    is_init_render = False

    # tree = comp.render().to_reactive_tree()
    # tree.print_tree()
    # tree.debug()
