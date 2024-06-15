# Built-in
import os
from pathlib import Path
import platform
import re

# Third-party
from colorama import just_fix_windows_console, Fore, Style
from tabulate import tabulate


# Metadata
__all__ = ["FXQUINOX_HOME", "FXQUINOX_TEMP", "FXQUINOX_APPDATA"]

# Intialize colorama
just_fix_windows_console()

# Get the current OS
_os_name = platform.system()
# _os_name = "Darwin"  # ? For debug purposes


# Package
def get_version_from_setup() -> str:
    """Get the version string from the `setup.py` file.

    Returns:
        str: The version string.
    """

    setup_file_path = Path(__file__).parents[1].joinpath("setup.py")
    version_match = re.compile(r"^.*version=['\"]([^'\"]*)['\"].*$", re.M)
    with open(setup_file_path, "r") as f:
        setup_contents = f.read()
    version = version_match.search(setup_contents)
    if version:
        return version.group(1)
    raise RuntimeError("Unable to find version string in 'setup.py'")


# Get the package name
FXQUINOX_NAME = __package__ if __package__ else "fxquinox"
FXQUINOX_VERSION = get_version_from_setup()


# Set up the environment variables
_home = Path.home()
FXQUINOX_HOME = os.environ["FXQUINOX_HOME"] = _home.resolve().as_posix()

if _os_name == "Windows":
    _temp_path = Path(os.getenv("TEMP", os.getenv("TMP", "/tmp")), FXQUINOX_NAME).resolve().as_posix()
else:
    _temp_path = Path(os.getenv("TMPDIR", "/tmp"), FXQUINOX_NAME).resolve().as_posix()
FXQUINOX_TEMP = os.environ["FXQUINOX_TEMP"] = _temp_path

if _os_name == "Windows":
    _appdata_path = Path(os.getenv("APPDATA", ""), FXQUINOX_NAME).resolve().as_posix()
else:
    _appdata_path = _home.joinpath(".fxquinox").resolve().as_posix()
FXQUINOX_APPDATA = os.environ["FXQUINOX_APPDATA"] = _appdata_path

FXQUINOX_LOGS = os.environ["FXQUINOX_LOGS"] = Path(FXQUINOX_APPDATA, "logs").resolve().as_posix()


def _test() -> None:
    """Tests the environment variables."""

    env_vars = [
        [f"{Fore.YELLOW}$FXQUINOX_HOME{Style.RESET_ALL}", f"{Fore.GREEN}{FXQUINOX_HOME}{Style.RESET_ALL}"],
        [f"{Fore.YELLOW}$FXQUINOX_TEMP{Style.RESET_ALL}", f"{Fore.GREEN}{FXQUINOX_TEMP}{Style.RESET_ALL}"],
        [f"{Fore.YELLOW}$FXQUINOX_APPDATA{Style.RESET_ALL}", f"{Fore.GREEN}{FXQUINOX_APPDATA}{Style.RESET_ALL}"],
        [f"{Fore.YELLOW}$FXQUINOX_LOGS{Style.RESET_ALL}", f"{Fore.GREEN}{FXQUINOX_LOGS}{Style.RESET_ALL}"],
    ]
    print(tabulate(env_vars, headers=["Variable", "Value"], tablefmt="pretty", colalign=("right", "left")))


if __name__ == "__main__":
    _test()
