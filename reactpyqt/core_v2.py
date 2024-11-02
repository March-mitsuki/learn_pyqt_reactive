from __future__ import annotations
from abc import ABC, abstractmethod


class VirtualWidget:
    def __init__(self) -> None:
        self.props = dict()


class Component(ABC):
    @abstractmethod
    def render(self) -> VirtualWidget | Component:
        pass
