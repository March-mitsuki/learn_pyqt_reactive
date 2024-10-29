from loguru import logger
from pathlib import Path
from datetime import date


def init_logger():
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    logger.add(
        log_path / f"{date.today().isoformat()}.log",
        rotation="1 day",
        retention="10 days",
        compression="zip",
        level="DEBUG",
        backtrace=True,
    )

    logger.info("Logger initialized")
