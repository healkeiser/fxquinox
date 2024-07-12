# Built-in
from pathlib import Path

# Third-party
from fxgui import fxicons, fxutils as fxguiutils
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *

# Internal
from fxquinox import fxlog, fxutils


# Log
_logger = fxlog.get_logger("fxmetadatatablewidget")
_logger.setLevel(fxlog.DEBUG)


class FXMetadataTableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(FXMetadataTableWidget, self).__init__(*args, **kwargs)

    def contextMenuEvent(self, event: QContextMenuEvent):
        """Creates a context menu for the table widget.

        Args:
            event (QContextMenuEvent): The context menu event.
        """

        # Create the context menu
        context_menu = QMenu(self)

        # Create actions for the context menu
        action_show_in_file_browser = fxguiutils.create_action(
            context_menu,
            "Show in File Browser",
            fxicons.get_icon("open_in_new"),
            lambda: fxutils.open_directory(self.currentItem().text()),
        )
        action_copy = fxguiutils.create_action(
            context_menu,
            "Copy",
            fxicons.get_icon("content_copy"),
            self._copy_to_clipboard,
            shortcut="Ctrl+C",
        )

        # Add actions to the context menu
        if Path(self.currentItem().text()).exists():  # Check if the metadata value is a valid path
            context_menu.addAction(action_show_in_file_browser)
            context_menu.addSeparator()
        context_menu.addAction(action_copy)

        # Show the context menu
        context_menu.exec_(event.globalPos())

    def _copy_to_clipboard(self):
        """Copies the selected item to the clipboard."""

        selected_item = self.currentItem()

        # Early return if no item is selected
        if selected_item is None:
            return

        clipboard = QApplication.clipboard()
        clipboard.setText(selected_item.text())
