# Built-in
from datetime import datetime
import logging
import logging.handlers
import os
from pathlib import Path

# Third-party
from colorama import just_fix_windows_console, Fore, Style

# Internal
from fxquinox import fxenvironment

# Metadata
__all__ = [
    # Globals
    "CRITICAL",
    "FATAL",
    "ERROR",
    "WARNING",
    "WARN",
    "INFO",
    "DEBUG",
    "NOTSET",
    # Functions
    "get_logger",
    "set_log_level",
]


# Globals
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

_LOG_DIRECTORY = Path(fxenvironment.FXQUINOX_LOGS)

# Initialize colorama
just_fix_windows_console()


class FXFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style="{", color=False, separator=False):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.LEVEL_COLORS = {
            logging.DEBUG: Fore.CYAN,
            logging.INFO: Fore.GREEN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.MAGENTA,
        }
        self.color = color
        self.separator = separator

    def format(self, record):
        # Define widths for various parts of the log message
        width_funcName = 35
        width_name = 15
        width_levelname = 8

        # Format line number with padding
        record.lineno = f"{record.lineno:<4}"

        # Handle separator if enabled
        if self.separator:
            separator = "-" * (85 + len(record.getMessage())) + "\n"
        else:
            separator = ""

        # Construct the log format string based on whether color is enabled
        if self.color:
            log_fmt = (
                f"{separator}{{asctime}} | {{name:>{width_name}s}} | {{lineno}} | "
                f"{Fore.YELLOW}{{funcName:<{width_funcName}s}}{Style.RESET_ALL} "
                f" | {Style.BRIGHT}{self.LEVEL_COLORS.get(record.levelno, Fore.WHITE)}"
                f"{{levelname:>{width_levelname}s}}{Style.RESET_ALL} | {{message}}"
            )
        else:
            log_fmt = (
                f"{separator}{{asctime}} | {{name:>{width_name}s}} | {{lineno}} | "
                f"{{funcName:<{width_funcName}s}} | "
                f"{{levelname:>{width_levelname}s}} | {{message}}"
            )

        # Create a new formatter with the constructed format string
        formatter = logging.Formatter(log_fmt, style="{", datefmt="%H:%S")
        return formatter.format(record)


class FXTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def rotation_filename(self, default_name: str) -> str:
        name, ext = os.path.splitext(default_name)
        return f"{name}.{self.suffix}{ext}"


def get_logger(logger_name: str, color: bool = True, separator: bool = False) -> logging.Logger:
    """Creates a custom logger with the specified name and returns it.

    Args:
        logger_name (str): The name of the logger.
        color (bool): Whether to enable color logging. Defaults to `True`.
        separator (bool): Whether to enable a separator between log messages.
            Defaults to `False`.

    Returns:
        logging.Logger: The custom logger.
    """

    # Check if the logger with the specified name already exists in the logger
    # dictionary
    if logger_name in logging.Logger.manager.loggerDict:
        return logging.getLogger(logger_name)

    # Formatter
    formatter = FXFormatter(color=color, separator=separator)
    logger = logging.getLogger(logger_name)

    # Console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # Save logs
    _LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file_path = _LOG_DIRECTORY / f"{logger_name}.{current_date}.log"

    # Create a file handler for logging with rotation at midnight (one file a day)
    file_handler = FXTimedRotatingFileHandler(log_file_path, "midnight", 1, 30, "utf-8")
    file_handler.setFormatter(FXFormatter(color=False, separator=True))
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False

    return logger


def set_log_level(level: int) -> None:
    """Sets the logging level for all instances of loggers created by the
    `FXFormatter` class.

    Args:
        level (int): The logging level to set.
    """

    for logger_name, logger in logging.Logger.manager.loggerDict.items():
        if isinstance(logger, logging.Logger) and logger.handlers:
            for handler in logger.handlers:
                if isinstance(handler.formatter, FXFormatter):
                    logger.setLevel(level)
                    handler.setLevel(level)


def clear_logs() -> None:
    """Clears the fxquinox log files."""

    for log_file in _LOG_DIRECTORY.iterdir():
        if log_file.is_file():
            log_file.unlink()
