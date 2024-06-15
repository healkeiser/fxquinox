# Built-in
import os
import logging
from typing import Optional

# Third-party
from colorama import just_fix_windows_console, Fore, Style


# Initialize colorama
just_fix_windows_console()


# Custom log formatter with explicit variable names
class FXColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record):
        level_color = self.LEVEL_COLORS.get(record.levelno, Fore.WHITE)
        log_format = (
            f"{'-' * 80}\n"
            f"{level_color}%(levelname)s | %(asctime)s | %(name)s | %(filename)s:%(lineno)d\n"
            f"{Style.BRIGHT}%(message)s{Style.RESET_ALL}"
        )
        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class FXFormatter(logging.Formatter):
    def format(self, record):
        log_format = (
            f"{'-' * 80}\n" f"%(levelname)s | %(asctime)s | %(name)s | %(filename)s:%(lineno)d\n" f"%(message)s"
        )
        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def get_logger(logger_name: str, force_color: Optional[bool] = None) -> logging.Logger:
    """Creates and returns a custom logger with a specified name and an optional
    forced color setting.

    Args:
        logger_name (str): The name of the logger to create.
        force_color (Optional[bool]): If set, forces the use of colored or
            plain text formatting regardless of terminal support. `True` forces
            colored formatting, `False` forces plain text, and `None` (default)
            auto-detects based on terminal capabilities. Defaults to `None`.

    Returns:
        logging.Logger: The configured logger instance.
    """

    # Create a custom logger
    custom_logger = logging.getLogger(logger_name)
    custom_logger.setLevel(logging.DEBUG)

    # Create console handler and set its level to debug
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Determine formatter based on `force_color` argument and terminal support
    if force_color is True:
        formatter = FXColoredFormatter()
    elif force_color is False:
        formatter = FXFormatter()
    else:
        # Terminal color support
        if (
            os.getenv("TERM")
            in ("xterm", "xterm-color", "xterm-256color", "screen", "screen-256color", "linux", "ansi")
            or "COLORTERM" in os.environ
        ):
            formatter = FXColoredFormatter()
        else:
            formatter = FXFormatter()

    # Add the chosen formatter to the console handler
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger if it doesn't already have handlers
    if not custom_logger.hasHandlers():
        custom_logger.addHandler(console_handler)

    # Prevent the logger from propagating to the root logger
    custom_logger.propagate = False

    return custom_logger


def set_log_level(level: int) -> None:
    """Sets the logging level for all instances of loggers created by the
    `FXColoredFormatter` or `FXFormatter` class.

    Args:
        level (int): The logging level to set. Use `logging.DEBUG`, `logging.INFO`, etc.
    """

    for logger_name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        if logger.handlers:
            for handler in logger.handlers:
                if isinstance(handler.formatter, (FXColoredFormatter, FXFormatter)):
                    logger.setLevel(level)
                    handler.setLevel(level)
