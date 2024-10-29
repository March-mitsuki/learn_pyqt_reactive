import sys
import ctypes
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QThreadPool
from loguru import logger

from logger import init_logger
from studio.main_window import MainWindow
from db.models import init_db


def handle_exception(exc_type, exc_value, exc_traceback):
    logger.exception(
        "Uncaught exception {}",
        exc_value,
        exc_info=(exc_type, exc_value, exc_traceback),
    )
    QMessageBox.critical(None, "Error", str(exc_value))


def handle_quit():
    QThreadPool.globalInstance().clear()


if __name__ == "__main__":
    init_logger()
    init_db()

    windll = ctypes.windll
    # if not windll.shell32.IsUserAnAdmin():
    #     logger.error("Please run this program as administrator")
    #     sys.exit(1)
    sys.excepthook = handle_exception

    app = QApplication(sys.argv)
    app.aboutToQuit.connect(handle_quit)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
