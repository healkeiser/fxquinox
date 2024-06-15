# Built-in
import os
from pathlib import Path
import platform


# Metadata
__all__ = ["FXQUINOX_HOME", "FXQUINOX_TEMP", "FXQUINOX_APPDATA"]

# Get the current OS
_os_name = platform.system()


# Set up the environment variables
FXQUINOX_HOME = os.environ["FXQUINOX_HOME"] = Path.home().resolve().as_posix()

if _os_name == "Windows":
    _temp_path = Path(os.getenv("TEMP", os.getenv("TMP", "/tmp"))).resolve().as_posix()
else:
    _temp_path = Path(os.getenv("TMPDIR", "/tmp")).resolve().as_posix()
FXQUINOX_TEMP = os.environ["FXQUINOX_TEMP"] = _temp_path

if _os_name == "Windows":
    _appdata_path = Path(os.getenv("APPDATA", "")).resolve().as_posix()
else:
    _appdata_path = Path.home().joinpath(".fxquinox").resolve().as_posix()
FXQUINOX_APPDATA = os.environ["FXQUINOX_APPDATA"] = _appdata_path


def _test() -> None:
    """Tests the environment variables."""

    print("Env: ", os.getenv("FXQUINOX_HOME"))
    print("Glo: ", FXQUINOX_HOME)
    print("Env: ", os.getenv("FXQUINOX_TEMP"))
    print("Glo: ", FXQUINOX_TEMP)
    print("Env: ", os.getenv("FXQUINOX_APPDATA"))
    print("Glo: ", FXQUINOX_APPDATA)


if __name__ == "__main__":
    _test()
