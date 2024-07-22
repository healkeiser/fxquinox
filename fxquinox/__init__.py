# Built-in
import os
import sys

if sys.version_info < (3, 11):
    os.environ["QT_API"] = "pyside2"
else:
    os.environ["QT_API"] = "pyside6"

# Internal
from fxquinox import fxcore, fxentities, fxenvironment, fxfiles, fxlog

__all__ = (
    "fxcore",
    "fxentities",
    "fxenvironment",
    "fxfiles",
    "fxlog",
)


# Set up the environment
fxenvironment.setup_environment()
