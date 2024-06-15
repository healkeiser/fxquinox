# Built-in
import os
from pathlib import Path
import platform

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

# Get the package name
PACKAGE_NAME = __package__ if __package__ else "fxquinox"

# Set up the environment variables
_home = Path.home()
FXQUINOX_HOME = os.environ["FXQUINOX_HOME"] = _home.resolve().as_posix()

if _os_name == "Windows":
    _temp_path = Path(os.getenv("TEMP", os.getenv("TMP", "/tmp")), PACKAGE_NAME).resolve().as_posix()
else:
    _temp_path = Path(os.getenv("TMPDIR", "/tmp"), PACKAGE_NAME).resolve().as_posix()
FXQUINOX_TEMP = os.environ["FXQUINOX_TEMP"] = _temp_path

if _os_name == "Windows":
    _appdata_path = Path(os.getenv("APPDATA", ""), PACKAGE_NAME).resolve().as_posix()
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
