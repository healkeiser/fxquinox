"""Runs after the UI is ready. You should use this script to set up
interactive since when it runs the UI and UI scripting is available,
and Houdini has loaded.
"""

# Internal
from fxquinox import fxlog


# Log
_logger = fxlog.get_logger("houdini.uiready")
_logger.setLevel(fxlog.DEBUG)
