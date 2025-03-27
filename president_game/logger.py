"""Gestion des logs"""

import logging
import sys
from pathlib import Path


def init_logger(
    log_file_path: Path | None = None,
    verbose: bool = False,
    quiet: bool = False,
) -> None:
    root_logger = logging.getLogger()
    # Si le logger est déjà défini, on passe
    if root_logger.handlers:
        return
    root_logger.setLevel(logging.DEBUG)

    # Stream handler
    console_handler = logging.StreamHandler(sys.stdout)

    if verbose:
        logging_level = logging.DEBUG
    elif quiet:
        logging_level = logging.ERROR
    else:
        logging_level = logging.INFO
    console_handler.setLevel(logging_level)
    console_formatter = logging.Formatter("%(asctime)s : %(levelname)-7s : %(message)s")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler
    if log_file_path is not None:
        if not log_file_path.parent.exists():
            log_file_path.parent.mkdir(parents=True)
        file_handler = logging.FileHandler(log_file_path, mode="w", encoding="utf-8")
        file_formatter = logging.Formatter("%(asctime)s : %(levelname)-7s : (%(filename)s:%(lineno)s) : %(message)s")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)

    sys.excepthook = lambda type, value, traceback: root_logger.exception(
        value, exc_info=(type, value, traceback)
    )  # cf https://stackoverflow.com/questions/6234405/logging-uncaught-exceptions-in-python
