# Built-in
import configparser
import os
from pathlib import Path
import psutil
import re
from typing import Optional

# Third-party
from qtpy.QtCore import QUrl
from qtpy.QtGui import QDesktopServices

# Internal
from fxquinox import fxenvironment


# String manipulation
def is_valid_string(input_string: str) -> bool:
    """Check if a string is valid for use. Match only alphanumeric characters,
    underscores, or hyphens.

    Args:
        input_string (str): The string to check.

    Returns:
        bool: `True` if the string is valid, `False` otherwise.
    """

    pattern = r"^[a-zA-Z0-9_-]*$"
    return bool(re.match(pattern, input_string))


def transform_to_valid_string(input_string: str) -> str:
    """Transform a string into a valid format by keeping only alphanumeric
    characters, underscores, or hyphens.

    Args:
        input_string (str): The string to transform.

    Returns:
        str: The transformed string with only valid characters.
    """

    pattern = r"[^a-zA-Z0-9_-]"
    valid_string = re.sub(pattern, "", input_string)
    return valid_string


# Configuration file handling
def update_configuration_file(file_name: str, section: str, option: str, value: str) -> None:
    """Updates or creates a value in a configuration file.

    Args:
        file_name (str): The name of the configuration file.
        section (str): The section in the configuration file.
        option (str): The option in the section.
        value (str): The value to update or create.

    Examples:
        >>> update_configuration_file("fxquinox.cfg", "settings", "theme", "dark")
    """

    config_path = Path(fxenvironment.FXQUINOX_APPDATA) / file_name

    # Initialize the configuration parser
    config = configparser.ConfigParser()

    # Load the configuration file if it exists, using the full path
    if config_path.is_file():
        config.read(config_path)

    # Check if the section exists, if not add it
    if not config.has_section(section):
        config.add_section(section)

    # Update the option with the new value
    config.set(section, option, value)

    # Write the changes back to the file, using the full path
    with open(config_path, "w") as config_file:
        config.write(config_file)


def get_configuration_file_value(file_name: str, section: str, option: str) -> Optional[str]:
    """Reads a value from a configuration file.

    Args:
        file_name (str): The name of the configuration file.
        section (str): The section in the configuration file.
        option (str): The option in the section.

    Returns:
        Optional[str]: The value of the option if found, `None` otherwise.
    """

    config_path = Path(fxenvironment.FXQUINOX_APPDATA) / file_name

    if not config_path.is_file():
        return None

    config = configparser.ConfigParser()
    config.read(config_path)

    # Check if the section and option exist, then return the value
    if config.has_section(section) and config.has_option(section, option):
        return config.get(section, option)
    else:
        return None


# PID Locking
def is_process_running(pid: int) -> bool:
    """Check if there's a running process with the given PID.

    Args:
        pid (int): The process ID to check.

    Returns:
        bool: `True` if the process is running, `False` otherwise.
    """

    try:
        p = psutil.Process(pid)
        return p.is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False


def check_and_create_lock(lock_file_path: str) -> bool:
    """Check for an existing lock and handle it appropriately.

    Args:
        lock_file_path (str): The path to the lock file.

    Returns:
        bool: `True` if the lock file was created, `False` otherwise (aka
            another instance is running).
    """

    lock_path = Path(lock_file_path)

    if lock_path.exists():
        pid = lock_path.read_text().strip()
        if pid and is_process_running(int(pid)):
            # Another instance is running
            return False
        else:
            # The process is not running > overwrite the lock file
            lock_path.write_text(str(os.getpid()))
            return True
    else:
        lock_path.write_text(str(os.getpid()))
        return True


def remove_lock(lock_file_path: str) -> None:
    """Remove the lock file.

    Args:
        lock_file_path (str): The path to the lock file.
    """

    lock_path = Path(lock_file_path)
    if lock_path.exists():
        lock_path.unlink()


# Directory
def open_directory(path: str) -> None:
    """Opens the given file or directory in the system file manager."""

    url = QUrl.fromLocalFile(path)
    QDesktopServices.openUrl(url)
