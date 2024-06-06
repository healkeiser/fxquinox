"""Examples on how to use the `fxgui` module."""

# Built-in
import os

os.environ["QT_API"] = "pyside2"

# Third-party
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *

from fxgui import fxwidgets, fxutils, fxdcc, fxstyle


###### CODE ####################################################################


class FXProjectBrowser(QWidget):
    """A simple project browser widget that displays a tree view of the project
    structure and allows the user to open files in the editor."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("FX Project Browser")
        self.resize(800, 600)

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Creates the UI elements and layouts."""

    def setup_connections(self):
        """Connects signals and slots for the widget."""
        pass
