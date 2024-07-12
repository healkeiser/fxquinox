# Built-in
import configparser
import os
from pathlib import Path
import psutil
import re
from typing import Optional, List, Dict

# Third-party
from qtpy.QtCore import QUrl
from qtpy.QtGui import QDesktopServices

# Internal
from fxquinox import fxenvironment, fxlog


# Log
_logger = fxlog.get_logger("fxutils")
_logger.setLevel(fxlog.DEBUG)


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
def update_configuration_file(file_name: str, sections_options_values: dict, temporary: bool = False) -> None:
    """Updates or creates multiple values in a configuration file based on a nested dictionary.

    Args:
        file_name (str): The name of the configuration file.
        sections_options_values (dict): A dictionary where keys are section
            names and values are dictionaries of options and their values to
            update or create.
        temporary (bool): If `True`, the configuration file will be stored in
            the temporary directory. Defaults to `False`.

    Examples:
        >>> config = {
        ...     "settings": {"theme": "dark", "language": "en"},
        ...     "database": {"host": "localhost", "port": "3306"},
        ... }
        >>> update_configuration_file("fxquinox.cfg", config)
    """

    if temporary:
        config_path = Path(fxenvironment.FXQUINOX_TEMP) / file_name
    else:
        config_path = Path(fxenvironment.FXQUINOX_APPDATA) / file_name

    # Initialize the configuration parser
    config = configparser.ConfigParser()

    # Load the configuration file if it exists
    if config_path.is_file():
        config.read(config_path)

    # Iterate over the sections and their options in the nested dictionary
    for section, options_values in sections_options_values.items():
        # Check if the section exists, if not add it
        if not config.has_section(section):
            config.add_section(section)

        # Iterate over the options and their values in the current section
        for option, value in options_values.items():
            config.set(section, option, value)

    # Write the changes back to the file, using the full path
    with open(config_path, "w") as config_file:
        config.write(config_file)


def get_configuration_file_values(
    file_name: str, sections_options: Dict[str, List[str]]
) -> Dict[str, Dict[str, Optional[str]]]:
    """Reads values from a configuration file for given sections and their options.

    Args:
        file_name (str): The name of the configuration file.
        sections_options (Dict[str, List[str]]): A dictionary where keys are
            section names and values are lists of options in those sections.

    Returns:
        Dict[str, Dict[str, Optional[str]]]: A nested dictionary where the
            first level keys are section names, and their values are
            dictionaries with options as keys and their values as values.
            If an option is not found, its value will be `None`.

    Examples:
        >>> config = {
        ...     "settings": ["theme", "language"],
        ...     "database": ["host", "port"],
        ... }
        >>> get_configuration_file_values("fxquinox.cfg", config)
        {
            'settings': {'theme': 'dark', 'language': 'en'},
            'database': {'host': 'localhost', 'port': '3306'}
        }
    """

    config_path = Path(fxenvironment.FXQUINOX_APPDATA) / file_name
    result = {
        section: {option: None for option in options} for section, options in sections_options.items()
    }  # Initialize all sections and options with None

    if not config_path.is_file():
        return result

    config = configparser.ConfigParser()
    config.read(config_path)

    for section, options in sections_options.items():
        if config.has_section(section):
            for option in options:
                if config.has_option(section, option):
                    # Update the result dictionary with the actual value from the config file
                    result[section][option] = config.get(section, option)

    return result


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


def check_and_create_lock_file(lock_file_path: str) -> bool:
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


def remove_lock_file(lock_file_path: str) -> None:
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
