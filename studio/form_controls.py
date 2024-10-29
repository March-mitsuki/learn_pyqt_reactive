from PyQt6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QLineEdit,
    QWidget,
    QComboBox,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal


class InputForm(QWidget):
    on_change = pyqtSignal(str)

    def __init__(self, label, placeholder):
        super().__init__()

        self.label = QLabel(label)
        self.label.setMinimumWidth(100)
        self.label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.textChanged.connect(self.on_change.emit)
        self.input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        self.setLayout(layout)


class SelectForm(QWidget):
    on_change = pyqtSignal(str)

    def __init__(self, label, options):
        super().__init__()

        self.label = QLabel(label)
        self.label.setMinimumWidth(100)
        self.label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.select = QComboBox()
        self.select.addItems(options)
        self.select.currentTextChanged.connect(self.on_change.emit)
        self.select.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.select)
        self.setLayout(layout)
