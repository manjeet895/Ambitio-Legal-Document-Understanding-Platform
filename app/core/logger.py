import logging
from logging import Logger


def configure_logger(level: str = "INFO") -> Logger:
    logger = logging.getLogger("ambitio_ai_platform")
    if not logger.handlers:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger
