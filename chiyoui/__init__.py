from .qss import QSS

# Make default PyQt6 widgets look same
DEFAULT_GLOBAL_QSS = QSS(
    {
        "QLabel": "margin: 3px;",
        "QComboBox": "padding: 3px 5px;",
        "QLineEdit": "margin: 3px;",
    }
)
