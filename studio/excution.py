import os
from loguru import logger
import time
from PyQt6.QtCore import pyqtSignal, QObject, QRunnable, pyqtSlot
import ctypes

from bot import NikkeBot
from db.models import OperationType, Operation, Task, Job


class JobSignlals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)


class JobExcution(QRunnable):
    def __init__(self, job: Job, sleep_between_tasks=1, sleep_between_operations=1):
        super().__init__()
        self.job = job
        self.sleep_between_tasks = sleep_between_tasks
        self.sleep_between_operations = sleep_between_operations

        self.bot = NikkeBot(cwd=os.getcwd(), window_name=job.window_name)

        self.signals = JobSignlals()

    @pyqtSlot()
    def run(self):
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                raise PermissionError("Please run this program as administrator")

            logger.info(f"Job Excution Thread Started: {self.job.name}")
            self.run_job()
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(e)

    def run_job(self):
        logger.info(f"Running Job: {self.job.name}")

        self.bot.set_foreground()
        for task in self.job.get_orded_tasks():
            if task.skip_this:
                logger.info(f"Skipping Task: {task.name}")
                continue
            self.run_task(task)
            time.sleep(self.sleep_between_tasks)

    def run_task(self, task: Task):
        logger.info(f"Running Task: {task.name}")

        for operation in task.get_orded_operations():
            if operation.skip_this:
                logger.info(f"Skipping Operation: {operation.name}")
                continue
            self.run_operation(operation)
            time.sleep(self.sleep_between_operations)

    def run_operation(self, operation: Operation):
        if operation.skip_this:
            # if operation is skipped, run_operation should not be called
            raise ValueError("Operation is skipped")

        ope_type = OperationType(operation.operation_type)
        if ope_type == OperationType.CLICK_IMG:
            logger.info(f"Runnning click image operation: {operation.name}")
            self.bot.click_img_with_retry(
                operation.click_img,
                screen=operation.screen_img,
                job_name=operation.name,
                click_times=operation.click_times,
            )
        elif ope_type == OperationType.CLICK_PERCENT:
            logger.info(f"Runnning click percent operation: {operation.name}")
            self.bot.click_percent_with_retry(
                operation.click_percent_x,
                operation.click_percent_y,
                screen=operation.click_percent_match_img,
                job_name=operation.name,
                click_times=operation.click_times,
            )
        elif ope_type == OperationType.WAIT:
            logger.info(f"Runnning wait operation: {operation.name}")
            if operation.is_implicity_wait:
                time.sleep(operation.wait_timeout)
            else:
                self.bot.wait_until_timeout(
                    operation.screen_img,
                    operation.wait_timeout,
                )
        else:
            self.signals.error.emit(ValueError(f"Unknown operation type: {ope_type}"))
