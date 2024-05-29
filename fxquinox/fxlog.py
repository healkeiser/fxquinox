# Built-in
import logging
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


def get_logger(logger_name):
    # Create a custom logger
    custom_logger = logging.getLogger(logger_name)
    custom_logger.setLevel(logging.DEBUG)

    # Create console handler and set its level to debug
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Add the custom formatter to the console handler
    console_handler.setFormatter(FXColoredFormatter())

    # Add the console handler to the logger if it doesn't already have handlers
    if not custom_logger.hasHandlers():
        custom_logger.addHandler(console_handler)

    # Prevent the logger from propagating to the root logger
    custom_logger.propagate = False

    return custom_logger


def main():
    # Create different loggers
    app_logger = get_logger("app_logger")
    module_logger = get_logger("module_logger")
    app_logger.debug("This is a debug message from the main application")
    app_logger.info("This is an info message from the main application")
    module_logger.warning("This is a warning message from a module")
    module_logger.error("This is an error message from a module")
    module_logger.critical("This is a critical message from a module")


if __name__ == "__main__":
    main()
