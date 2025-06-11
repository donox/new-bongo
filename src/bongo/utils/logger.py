# src/bongo/utils/logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Dict, Any


def setup_logging(config: Dict[str, Any] = None):
    """
    Configures the root logger for the application.

    This function sets up two handlers:
    1. A StreamHandler to print logs to the console (stdout).
    2. A RotatingFileHandler to write logs to a file, with automatic rotation.

    The log level and file path are determined by the provided configuration,
    with sensible defaults.

    Args:
        config (Dict[str, Any], optional): A dictionary containing logging settings,
                                            typically loaded from a config file.
                                            Expected keys: 'level', 'filepath'.
                                            Defaults to None.
    """
    if config is None:
        config = {}

    # Determine logging level: from config, or default to INFO
    log_level_str = config.get("level", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Determine log file path: from config, or default to 'bongo.log'
    log_filepath = config.get("filepath", "bongo.log")

    # Get the root logger
    root_logger = logging.getLogger("bongo")
    root_logger.setLevel(log_level)

    # Prevent adding duplicate handlers if this function is called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Create a rotating file handler
    try:
        # 1MB per file, keeping up to 5 backup files
        file_handler = RotatingFileHandler(log_filepath, maxBytes=1024 * 1024, backupCount=5)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except (IOError, PermissionError) as e:
        root_logger.error(f"Could not open log file '{log_filepath}': {e}. Logging to console only.")

    root_logger.info(f"Logging initialized. Level: {log_level_str}, File: '{log_filepath}'")

