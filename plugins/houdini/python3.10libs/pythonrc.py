"""Houdini runs this script (if it exists) very early in the startup sequence,
before the UI is available and before assets are loaded. If you don’t need
the UI or assets, or if you want to configure the UI or asset loading before
it starts, you can use this script. Otherwise, use `ready.py` or `uiready.py`
instead.
"""

# Third-party
import hou

# Internal
from fxquinox import fxlog


# Log
_logger = fxlog.get_logger("houdini.pythonrc")
_logger.setLevel(fxlog.DEBUG)


def _set_solaris_default_prim_paths() -> None:
    """Set the default Solaris USD primitive paths."""

    hou.lop.setDefaultNewPrimPath("/world/$OS")
    hou.lop.setDefaultCamerasPrimPath("/world/cam/$OS")
    hou.lop.setDefaultLightsPrimPath("/world/lgt/$OS")

    _logger.info("Set Solaris default primitive paths")
    _logger.debug(f"New prim path: '{hou.lop.defaultNewPrimPath()}'")
    _logger.debug(f"Cameras prim path: '{hou.lop.defaultCamerasPrimPath()}'")
    _logger.debug(f"Lights prim path: '{hou.lop.defaultLightsPrimPath()}'")


if __name__ == "__main__":
    _set_solaris_default_prim_paths()
