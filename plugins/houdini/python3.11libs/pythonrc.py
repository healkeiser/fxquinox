"""Houdini runs this script (if it exists) very early in the startup sequence,
before the UI is available and before assets are loaded. If you don’t need
the UI or assets, or if you want to configure the UI or asset loading before
it starts, you can use this script. Otherwise, use `ready.py` or `uiready.py`
instead.
"""

# Third-party
from curses import meta
import hou

# Internal
from fxquinox import fxlog, fxenvironment, fxfiles


# Log
_logger = fxlog.get_logger("houdini.pythonrc")
_logger.setLevel(fxlog.DEBUG)

# Global
metadata = None


def _set_solaris_default_prim_paths() -> None:
    """Set the default Solaris USD primitive paths."""

    hou.lop.setDefaultNewPrimPath("/world/$OS")
    hou.lop.setDefaultCamerasPrimPath("/world/cam/")
    hou.lop.setDefaultLightsPrimPath("/world/lgt/")

    _logger.info("Set Solaris default primitive paths")
    _logger.debug(f"New prim path: '{hou.lop.defaultNewPrimPath()}'")
    _logger.debug(f"Cameras prim path: '{hou.lop.defaultCamerasPrimPath()}'")
    _logger.debug(f"Lights prim path: '{hou.lop.defaultLightsPrimPath()}'")


def _retrieve_metadata_before_save(event_type):
    global metadata
    if event_type == hou.hipFileEventType.BeforeSave:
        _logger.debug(f"Triggered `BeforeSave`: '{hou.hipFile.path()}'")
        metadata = fxfiles.get_all_metadata(hou.hipFile.path())


def _set_metadata_after_save(event_type):
    global metadata
    if event_type == hou.hipFileEventType.AfterSave:
        _logger.debug(f"Triggered `AfterSave`: '{hou.hipFile.path()}'")
        print(type(metadata))
        print(metadata)


if __name__ == "__main__":
    _set_solaris_default_prim_paths()
    hou.hipFile.addEventCallback(_retrieve_metadata_before_save)
    hou.hipFile.addEventCallback(_set_metadata_after_save)
