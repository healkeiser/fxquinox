# Built-in
from pathlib import Path
from functools import partial
import sys
import subprocess
import textwrap
from turtle import position
from typing import Optional, Dict

# Third-party
from fxgui import fxwidgets, fxicons, fxstyle, fxutils as fxguiutils
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *
import yaml

# Internal
from fxquinox import fxenvironment, fxlog, fxutils, fxcore
from fxquinox.ui.fxwidgets import fxprojectbrowser
from fxquinox.ui.fxwidgets.fxdialog import FXDialog


# Log
_logger = fxlog.get_logger("_fxlauncher")
_logger.setLevel(fxlog.DEBUG)


class FXLauncherWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.top_widget = None
        self.tray_icon = fxwidgets.FXSystemTray(
            icon=QIcon(str(Path(fxenvironment._FQUINOX_IMAGES) / "fxquinox_logo_light.svg"))
        )
        self.setup_tray_icon()

    def setup_tray_icon(self):
        menu = self.tray_icon.tray_menu
        action_quit = self.tray_icon.quit_action

        action_refresh = QAction("Refresh", self)
        action_refresh.triggered.connect(self.on_refresh)

        menu.insertAction(action_quit, action_refresh)

        # action_quit = menu.addAction("Quit")
        # action_quit.triggered.connect(fxwidgets.FXApplication.instance().quit)

        # self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def on_refresh(self):
        if not self.top_widget:
            self.top_widget = QWidget()
            self.top_widget.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
            self.top_widget.setAttribute(Qt.WA_TranslucentBackground)
            self.top_widget.setWindowOpacity(0.8)  # Adjust opacity as needed

        # Position and size logic here
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_center = screen_geometry.center()
        desired_size = QSize(200, 100)  # Example size
        self.top_widget.resize(desired_size)

        # Calculate the top-left position for the widget to be centered
        top_left_position = QPoint(
            screen_center.x() - desired_size.width() / 2, screen_center.y() - desired_size.height() / 2
        )

        self.top_widget.move(top_left_position)
        self.top_widget.show()


if __name__ == "__main__":
    app = fxwidgets.FXApplication().instance()
    widget = FXLauncherWidget()
    sys.exit(app.exec_())
