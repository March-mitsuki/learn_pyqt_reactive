class QSS:
    def __init__(self, initial_qss=None):
        if isinstance(initial_qss, dict):
            self._qss = initial_qss
        else:
            self._qss = dict()

    def __str__(self):
        return "\n".join([f"{k} {{{v}}}" for k, v in self._qss.items()])

    def to_str(self):
        return str(self)

    def add(self, selector, value):
        self._qss[selector] = value

    def remove(self, selector):
        self._qss.pop(selector, None)

    def clear(self):
        self._qss.clear()

    def get(self, selector):
        return self._qss.get(selector)

    def set(self, selector, value):
        self._qss[selector] = value
