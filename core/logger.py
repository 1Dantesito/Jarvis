import logging
import sys
import time
from typing import Optional

def setup_logger(name: str = "JARVIS") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_logger("JARVIS")

class PerformanceTimer:
    def __init__(self, operation_name: str, logger_instance: Optional[logging.Logger] = None):
        self.operation_name = operation_name
        self.logger = logger_instance or logger
        self.start_time = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_ms = (time.perf_counter() - self.start_time) * 1000
        status = "FALLO" if exc_type else "OK"
        self.logger.info(f"[{self.operation_name}] {status} en {elapsed_ms:.1f}ms")
