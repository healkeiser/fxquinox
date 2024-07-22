# Built-in
import os
from pathlib import Path
import sys
from typing import Optional

if sys.version_info < (3, 11):
    os.environ["QT_API"] = "pyside2"
else:
    os.environ["QT_API"] = "pyside6"

# Third-party
from fxgui import fxwidgets, fxicons, fxutils as fxguiutils
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *
import yaml

# Internal
from fxquinox import fxentities, fxenvironment, fxfiles, fxlog


# Log
_logger = fxlog.get_logger("fxsaveworkfile")
_logger.setLevel(fxlog.DEBUG)


class FXSaveWorkfile(QDialog):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        dcc: fxentities.DCC = fxentities.DCC.standalone,
        entity: Optional[str] = None,
        asset: Optional[str] = None,
        asset_path: Optional[str] = None,
        sequence: Optional[str] = None,
        sequence_path: Optional[str] = None,
        shot: Optional[str] = None,
        shot_path: Optional[str] = None,
        step: Optional[str] = None,
        step_path: Optional[str] = None,
        task: Optional[str] = None,
        task_path: Optional[str] = None,
    ):
        super().__init__(parent)

        # Attributes
        self.dcc: fxentities.DCC = dcc
        self.entity: str = None
        self.asset = None
        self.asset_path: str = None
        self.sequence: str = None
        self.sequence_path: str = None
        self.shot: str = None
        self.shot_path: str = None
        self.step: str = None
        self.step_path: str = None
        self.task: str = None
        self.task_path: str = None

        self.workfile: Optional[str] = None
        self.workfile_path: Optional[str] = None
        self.new_workfile: Optional[str] = None
        self.new_workfile_path: Optional[str] = None

        # Methods
        self.setModal(True)

        self._create_ui()
        self._rename_ui()
        self._modify_ui()
        self._handle_connections()
        self._toggle_next_available_version()
        self._toggle_save_button()
        self._get_current_workfile()

    def _create_ui(self) -> None:
        """Create the UI for the Save Workfile dialog."""

        ui_file = Path(fxenvironment._FXQUINOX_UI) / "save_workfile.ui"
        self.ui = fxguiutils.load_ui(self, str(ui_file))
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)
        self.setWindowTitle("Save Workfile")
        self.resize(500, 125)

    def _rename_ui(self) -> None:
        """Rename the UI elements for the Save Workfile dialog."""

        self.label_icon_version = self.ui.label_icon_version
        self.label_version = self.ui.label_version
        self.spinbox_version = self.ui.spinbox_version
        self.checkbox_next_available_version = (
            self.ui.checkbox_next_available_version
        )
        #
        self.label_icon_workfile = self.ui.label_icon_workfile
        self.label_workfile = self.ui.label_workfile
        self.line_edit_workfile = self.ui.line_edit_workfile
        self.button_box: QDialogButtonBox = self.ui.button_box
        #
        self.label_icon_path = self.ui.label_icon_path
        self.label_path = self.ui.label_path
        self.line_edit_path = self.ui.line_edit_path

    def _modify_ui(self) -> None:
        """Modify the UI elements for the Save Workfile dialog."""

        #
        self.label_icon_version.setPixmap(fxicons.get_pixmap("tag", width=18))
        self.label_icon_workfile.setPixmap(
            fxicons.get_pixmap("description", width=18)
        )
        self.label_icon_path.setPixmap(fxicons.get_pixmap("folder", width=18))

        # Contains some slots connections, to avoid iterating multiple times
        # over the buttons
        for button in self.button_box.buttons():
            role = self.button_box.buttonRole(button)
            if role == QDialogButtonBox.AcceptRole:
                button.setIcon(fxicons.get_icon("save", color="#8fc550"))
                button.setText("Save")
                # Create step
                # button.clicked.connect(self._create_step)
            elif role == QDialogButtonBox.RejectRole:
                button.setIcon(fxicons.get_icon("close", color="#ec0811"))
                # Close
                button.clicked.connect(self.close)

    def _handle_connections(self) -> None:
        self.checkbox_next_available_version.stateChanged.connect(
            self._toggle_next_available_version
        )
        self.line_edit_path.textChanged.connect(self._toggle_save_button)

    def _toggle_next_available_version(self) -> None:
        """Toggle the next available version spinbox."""

        self.spinbox_version.setEnabled(
            not self.checkbox_next_available_version.isChecked()
        )

    def _toggle_save_button(self) -> None:
        """Toggle the save button."""

        if self.line_edit_path.text() and self.line_edit_workfile.text():
            self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
        else:
            self.button_box.button(QDialogButtonBox.Save).setEnabled(False)

    def _get_current_workfile_houdini(self) -> None:
        """Get the current workfile in Houdini."""

        try:
            import hou  # type: ignore

            path_workfile = Path(hou.hipFile.name())
            path_workfile_path = Path(hou.hipFile.path())

            self.workfile = str(path_workfile)
            self.workfile_path = str(path_workfile_path.as_posix())

            self.line_edit_workfile.setText(self.workfile)
            self.line_edit_path.setText(self.workfile_path)
        except ImportError as exception:
            _logger.error(f"Error: {str(exception)}")

    def _get_current_workfile(self) -> None:
        """Get the current workfile."""

        _logger.debug(f"DCC: {self.dcc}")
        _logger.debug(f"Getting current workfile...")

        if self.dcc == fxentities.DCC.standalone:
            pass

        elif self.dcc == fxentities.DCC.blender:
            pass

        elif self.dcc == fxentities.DCC.houdini:
            self._get_current_workfile_houdini()

        elif self.dcc == fxentities.DCC.maya:
            pass

        elif self.dcc == fxentities.DCC.nuke:
            pass

        elif self.dcc == fxentities.DCC.photoshop:
            pass

        self._get_current_version()

    def _get_current_version(self) -> None:

        workfile = self.line_edit_workfile.text()
        version = fxfiles.find_version_in_filename(workfile)

        if version:
            self.spinbox_version.setValue(version)

    def _save_workfile_houdini(self, file_path: str) -> None:
        """Opens the workfile in Houdini.

        Args:
            file_path (str): The path to the workfile.
        """

        try:
            import hou  # type: ignore

            hou.hipFile.save(file_path)
            self.close()
        except ImportError as exception:
            _logger.error(f"Error: {str(exception)}")

    def _save_workfile(self) -> None:
        """Save the workfile."""

        if self.dcc == fxentities.DCC.standalone:
            pass

        elif self.dcc == fxentities.DCC.blender:
            pass

        elif self.dcc == fxentities.DCC.houdini:
            pass

        elif self.dcc == fxentities.DCC.maya:
            pass

        elif self.dcc == fxentities.DCC.nuke:
            pass

        elif self.dcc == fxentities.DCC.photoshop:
            pass


def run_save_worfile(
    parent: Optional[QWidget] = None,
    quit_on_last_window_closed: bool = True,
    dcc: fxentities.DCC = fxentities.DCC.standalone,
) -> QWidget:
    # Application
    if not parent:
        _fix = QUiLoader()  # XXX: This is a PySide6 bug
        app = fxwidgets.FXApplication.instance()
        app.setQuitOnLastWindowClosed(quit_on_last_window_closed)

    # ui_file = Path(fxenvironment._FXQUINOX_UI) / "save_workfile.ui"
    icon_path = (
        Path(fxenvironment._FQUINOX_IMAGES)
        / "fxquinox_logo_background_light.svg"
    )

    widget = FXSaveWorkfile(parent=parent, dcc=dcc)
    widget.setWindowTitle("Save Workfile")
    widget.setWindowIcon(QIcon(str(icon_path)))

    widget.show()
    # window.setStyleSheet(fxstyle.load_stylesheet())

    if not parent:
        app.exec_()

    return widget


if __name__ == "__main__":
    run_save_worfile()
