from PyQt6.QtWidgets import QLabel, QLineEdit, QComboBox, QSizePolicy
from PyQt6.QtCore import pyqtSignal
from loguru import logger
from marshmallow import Schema, ValidationError

from .layout import HBox, VBox


class Form(VBox):
    _name = "form"
    _on_submit = pyqtSignal(dict)

    def __init__(
        self,
        *args,
        on_submit=None,
        validation_schema: Schema | None = None,
        on_validate_error=None,
        **kwargs,
    ):
        logger.debug("Form init with args: '{}' and kwargs: '{}'", args, kwargs)

        super().__init__(*args, **kwargs)
        self.fields = args
        self.submit_button = None
        self.on_submit = on_submit
        self.validation_schema = validation_schema
        self.on_validate_error = on_validate_error

        for field in self.fields:
            if field._name == "button" and field.type == "submit":
                self.submit_button = field
                self.submit_button.reconnect(self.handle_submit)
                break

    def handle_submit(self):
        logger.debug("Form submitted")

        try:
            values = self.get_values()
        except ValidationError:
            return

        if self.on_submit:
            self.on_submit(values)
        else:
            self._on_submit.emit(values)

    def get_values(self):
        result = {}

        for field in self.fields:
            if getattr(field, "form_field", None):
                result[field.form_field] = field.get_value()
            if getattr(field, "form_validator", None):
                if not field.form_validator(result[field.form_field]):
                    if self.on_validate_error:
                        errors = {field.form_field: "Validation failed"}
                        self.on_validate_error(errors)
                        logger.debug(f"Validation failed: {errors}")
                        raise ValidationError(errors)

        if hasattr(self, "validation_schema") and self.on_validate_error:
            err = self.validation_schema.validate(result)
            if len(err) > 0:
                self.on_validate_error(err)
                logger.debug(f"Validation failed using schema: {err}")
                raise ValidationError(err)

        return result


class Input(HBox):
    """
    self.label: QLabel\n
    self.input: QLineEdit
    """

    _name = "input"
    _on_edit = pyqtSignal(str)
    _on_change = pyqtSignal(str)

    def __init__(
        self,
        *args,
        label: str,
        placeholder: str,
        on_edit=None,
        on_change=None,
        form_field=None,
        form_validator=None,
        **kwargs,
    ):
        logger.debug(
            "Input init with label: '{}' and placeholder: '{}'", label, placeholder
        )

        super().__init__(*args, **kwargs)
        self.form_field = form_field
        self.form_validator = form_validator
        self.on_edit = on_edit
        self.on_change = on_change

        self.label = QLabel(label, self)
        self.label.setMinimumWidth(100)
        self.label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.input = QLineEdit(self)
        self.input.setPlaceholderText(placeholder)
        self.input.textEdited.connect(self.handle_edit)
        self.input.textChanged.connect(self.handle_change)
        self.input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.layout().addWidget(self.label)
        self.layout().addWidget(self.input)

    def handle_edit(self, text):
        if self.on_edit:
            self.on_edit(text)
        else:
            self._on_edit.emit(text)

    def handle_change(self, text):
        if self.on_change:
            self.on_change(text)
        else:
            self._on_change.emit(text)

    def get_value(self):
        return self.input.text()


class NumberInput(Input):
    _name = "number_input"
    _on_change = pyqtSignal(int)
    _on_edit = pyqtSignal(int)

    def handle_edit(self, text):
        value = 0
        try:
            value = int(text)
        except ValueError:
            pass

        if self.on_edit:
            self.on_edit(value)
        else:
            self._on_edit.emit(value)

    def handle_change(self, text):
        value = 0
        try:
            value = int(text)
        except ValueError:
            pass

        if self.on_change:
            self.on_change(value)
        else:
            self._on_change.emit(value)

    def get_value(self):
        try:
            return int(self.input.text())
        except ValueError:
            return 0


class Select(HBox):
    """
    self.label: QLabel\n
    self.select: QComboBox
    """

    _name = "select"
    _on_change = pyqtSignal(str)

    def __init__(
        self,
        *args,
        label: str,
        options: list[tuple[str, str]],
        on_change=None,
        form_field=None,
        form_validator=None,
        **kwargs,
    ):
        logger.debug("Select init with label: '{}' and options: '{}'", label, options)

        super().__init__(*args, **kwargs)
        self.form_field = form_field
        self.form_validator = form_validator

        self.label = QLabel(label)
        self.label.setMinimumWidth(100)
        self.label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.select = QComboBox()
        for option in options:
            self.select.addItem(option[0], option[1])
        self.select.currentTextChanged.connect(on_change or self._on_change.emit)
        self.select.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        self.layout().addWidget(self.label)
        self.layout().addWidget(self.select)

    def get_value(self):
        return self.select.currentData()
