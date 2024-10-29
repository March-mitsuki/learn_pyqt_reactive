from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton


class MultiInputDialog(QDialog):
    def __init__(self, window_title, field_names: list[str]):
        self.ok = False
        super().__init__()
        self.setWindowTitle(window_title)

        layout = QVBoxLayout()

        for field_name in field_names:
            input_field = QLineEdit(self)
            layout.addWidget(QLabel(f"{field_name}:"))
            layout.addWidget(input_field)

        self.ok_button = QPushButton("确定", self)
        self.ok_button.clicked.connect(self.on_ok)

        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def on_ok(self):
        self.ok = True
        self.accept()

    def get_values(self):
        layout = self.layout()
        values = []
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QLineEdit):
                values.append(widget.text())
        self.close()
        return values, self.ok
