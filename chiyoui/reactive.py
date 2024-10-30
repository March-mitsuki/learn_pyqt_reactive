from PyQt6.QtCore import pyqtSignal, QObject


class Signal(QObject):
    on_change = pyqtSignal(object)

    def __init__(self, initial_signal):
        super().__init__()
        self._signal = initial_signal

    def set(self, new_signal):
        """
        Parameters:
            new_signal: Union[object, Callable[[object], object]]
        """
        if callable(new_signal):
            self._signal = new_signal(self._signal)
        else:
            self._signal = new_signal
        self.on_change.emit(self._signal)

    def current(self):
        return self._signal


class Ref:
    def __init__(self):
        self.current = None


def use_signal(initial_signal):
    return Signal(initial_signal)


def use_ref():
    return Ref()
