"""Runs at startup after all non-graphical components of Houdini has been
loaded.
The difference between `pythonrc.py` and `ready.py` is that `pythonrc.py`
executes before HDAs are loaded and `ready.py` executes after HDAs are loaded.
"""

# Third-party
import hou

# Internal
from fxquinox import fxlog
from plugins.houdini.python import contextoptions


# Log
_logger = fxlog.get_logger("houdini.ready")
_logger.setLevel(fxlog.DEBUG)


# Context options
def set_context_options() -> None:
    """Set the context options for the current environment."""

    contextoptions.set_context_options()
    contextoptions.add_context_options_callbacks()


def set_context_options_callback(event_type: hou.hipFileEventType) -> None:
    """Callback invoked on scene load triggering the title update to reflect the current
    project and ShotGrid config.

    Args:
        event_type (hou.hipFileEventType): Event type to filter.
    """

    if not event_type == hou.hipFileEventType.AfterLoad:
        return

    _logger.debug(f"Triggered `hipFileEventType.AfterLoad`")
    set_context_options()


if __name__ == "__main__":
    set_context_options()  # Run a first time
    hou.hipFile.addEventCallback(set_context_options_callback)  # Set callback to update on scene load
