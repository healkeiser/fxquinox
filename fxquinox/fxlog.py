# Built-in
import logging
import os
from pathlib import Path
from typing import Optional

# Third-party
from colorama import just_fix_windows_console, Fore, Style

# Internal
from fxquinox import fxenvironment


# Initialize colorama
just_fix_windows_console()


class FXFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def __init__(self, color: Optional[bool] = False):
        if color:
            log_format = (
                f"{'-' * 80}\n"
                f"%(levelname)s | %(asctime)s | %(name)s | %(filename)s:%(lineno)d\n"
                f"{Style.BRIGHT}%(message)s{Style.RESET_ALL}"
            )
        else:
            log_format = (
                f"{'-' * 80}\n" f"%(levelname)s | %(asctime)s | %(name)s | %(filename)s:%(lineno)d\n" f"%(message)s"
            )
        super().__init__(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        self.color = color

    def format(self, record: logging.LogRecord) -> str:
        """Formats the log record based on the current settings.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log message.
        """

        original_levelname = record.levelname  # Store the original levelname
        if self.color:
            record.levelname = self.LEVEL_COLORS.get(record.levelno, Fore.WHITE) + record.levelname
        formatted_message = super().format(record)
        record.levelname = original_levelname  # Restore the original levelname
        return formatted_message


def get_logger(logger_name: str, force_color: Optional[bool] = None) -> logging.Logger:
    """Creates a custom logger with the specified name and returns it.

    Args:
        logger_name (str): The name of the logger.
        force_color (Optional[bool]): Whether to force color logging.
            Defaults to `None`.

    Returns:
        logging.Logger: The custom logger.
    """

    # Check if the logger with the specified name already exists in the logger dictionary
    if logger_name in logging.Logger.manager.loggerDict:
        # If it exists, return the existing logger
        return logging.getLogger(logger_name)

    # Create a new logger with the specified name
    custom_logger = logging.getLogger(logger_name)

    # Create a console handler to output logs to the console
    console_handler = logging.StreamHandler()

    # Determine if colored output is forced or supported by the terminal
    if force_color or (
        force_color is None
        and (
            os.getenv("TERM")
            in ("xterm", "xterm-color", "xterm-256color", "screen", "screen-256color", "linux", "ansi")
            or "COLORTERM" in os.environ
        )
    ):
        # If color is supported or forced, use a colored formatter
        formatter = FXFormatter(color=True)
    else:
        # Otherwise, use a standard formatter without color
        formatter = FXFormatter()

    # Set the formatter for the console handler
    console_handler.setFormatter(formatter)

    # Define the directory path for log files
    log_directory = Path(fxenvironment.FXQUINOX_APPDATA) / "logs"

    # Create the log directory if it does not exist
    if not log_directory.exists():
        log_directory.mkdir(parents=True, exist_ok=True)

    # Define the path for the log file
    log_file_path = log_directory / f"{logger_name}.log"

    # Create a file handler for logging with rotation at midnight (one file a day)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file_path, when="midnight", interval=1, backupCount=30, encoding="utf-8"
    )

    # Set a non-colored formatter for the file handler
    file_handler.setFormatter(FXFormatter(color=False))

    # Set the logging level for the file handler
    file_handler.setLevel(logging.DEBUG)

    # Add the console and file handlers to the custom logger
    custom_logger.addHandler(console_handler)
    custom_logger.addHandler(file_handler)

    # Prevent the custom logger from propagating logs to the root logger
    custom_logger.propagate = False

    return custom_logger


def set_log_level(level: int) -> None:
    """Sets the logging level for all instances of loggers created by the
    `FXColoredFormatter` or `FXFormatter` class.

    Args:
        level (int): The logging level to set. Use `logging.DEBUG`, `logging.INFO`, etc.
    """

    for logger_name, logger in logging.Logger.manager.loggerDict.items():
        if isinstance(logger, logging.Logger) and logger.handlers:
            for handler in logger.handlers:
                if isinstance(handler.formatter, FXFormatter):
                    logger.setLevel(level)
                    handler.setLevel(level)
