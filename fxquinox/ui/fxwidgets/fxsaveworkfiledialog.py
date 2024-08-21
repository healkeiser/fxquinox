# Built-in
import getpass
import mss
import os
from pathlib import Path
import re
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

# Internal
from fxquinox import fxentities, fxenvironment, fxfiles, fxlog, fxutils
from fxquinox.ui.fxwidgets.fxscreencapturewindow import FXScreenCaptureWindow


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

        self.screen_capture_window: QMainWindow = None

        # Methods
        self.setModal(True)

        self._create_ui()
        self._rename_ui()
        self._modify_ui()
        self._handle_connections()
        self._toggle_next_available_version()
        self._toggle_save_button()
        self._get_current_workfile()
        self._build_save_path()

    def _create_ui(self) -> None:
        """Create the UI for the Save Workfile dialog."""

        ui_file = Path(fxenvironment._FXQUINOX_UI) / "save_workfile.ui"
        self.ui = fxguiutils.load_ui(self, str(ui_file))
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)
        self.setWindowTitle("Save Workfile")
        self.resize(900, 200)

    def _rename_ui(self) -> None:
        """Rename the UI elements for the Save Workfile dialog."""

        self.label_icon_version: QLabel = self.ui.label_icon_version
        self.label_version: QLabel = self.ui.label_version
        self.spinbox_version: QSpinBox = self.ui.spinbox_version
        self.checkbox_next_available_version: QCheckBox = (
            self.ui.checkbox_next_available_version
        )
        #
        self.label_icon_workfile: QLabel = self.ui.label_icon_workfile
        self.label_workfile: QLabel = self.ui.label_workfile
        self.line_edit_workfile: QLineEdit = self.ui.line_edit_workfile
        self.button_box: QDialogButtonBox = self.ui.button_box
        #
        self.label_icon_path: QLabel = self.ui.label_icon_path
        self.label_path: QLabel = self.ui.label_path
        self.line_edit_path: QLineEdit = self.ui.line_edit_path
        #
        self.label_icon_to_save: QLabel = self.ui.label_icon_to_save
        self.label_to_save: QLabel = self.ui.label_to_save
        self.line_edit_to_save: QLineEdit = self.ui.line_edit_to_save
        #
        self.label_icon_thumbnail: QLabel = self.ui.label_icon_thumbnail
        self.label_thumbnail: QLabel = self.ui.label_thumbnail
        self.line_edit_thumbnail: QLineEdit = self.ui.line_edit_thumbnail
        self.button_pick_thumbnail: QPushButton = self.ui.button_pick_thumbnail
        self.button_discard_thumbnail: QPushButton = (
            self.ui.button_discard_thumbnail
        )
        self.button_capture_thumbnail: QPushButton = (
            self.ui.button_capture_thumbnail
        )
        self.button_preview_thumbnail: QPushButton = (
            self.ui.button_preview_thumbnail
        )
        #
        self.label_comment: QLabel = self.ui.label_comment
        self.label_icon_comment: QLabel = self.ui.label_icon_comment
        self.text_edit_comment: QTextEdit = self.ui.text_edit_comment

    def _modify_ui(self) -> None:
        """Modify the UI elements for the Save Workfile dialog."""

        #
        self.label_icon_version.setPixmap(fxicons.get_pixmap("tag", width=18))
        self.label_icon_workfile.setPixmap(
            fxicons.get_pixmap("description", width=18)
        )
        self.label_icon_path.setPixmap(fxicons.get_pixmap("folder", width=18))
        self.label_icon_to_save.setPixmap(fxicons.get_pixmap("save", width=18))
        self.label_icon_thumbnail.setPixmap(
            fxicons.get_pixmap("camera", width=18)
        )
        self.label_icon_comment.setPixmap(
            fxicons.get_pixmap("comment", width=18)
        )

        self.button_pick_thumbnail.setIcon(fxicons.get_icon("folder_open"))
        self.button_capture_thumbnail.setIcon(fxicons.get_icon("fit_screen"))
        self.button_discard_thumbnail.setIcon(fxicons.get_icon("delete"))
        self.button_preview_thumbnail.setIcon(fxicons.get_icon("preview"))

        # Contains some slots connections, to avoid iterating multiple times
        # over the buttons
        for button in self.button_box.buttons():
            role = self.button_box.buttonRole(button)
            if role == QDialogButtonBox.AcceptRole:
                button.setIcon(fxicons.get_icon("save", color="#8fc550"))
                button.setText("Save")
                # Create step
                button.clicked.connect(self._save_workfile)
            elif role == QDialogButtonBox.RejectRole:
                button.setIcon(fxicons.get_icon("close", color="#ec0811"))
                # Close
                button.clicked.connect(self.close)

    def _handle_connections(self) -> None:
        self.checkbox_next_available_version.stateChanged.connect(
            self._toggle_next_available_version
        )
        self.checkbox_next_available_version.stateChanged.connect(
            self._get_current_version
        )
        self.line_edit_path.textChanged.connect(self._toggle_save_button)
        self.spinbox_version.valueChanged.connect(self._build_save_path)
        self.button_pick_thumbnail.clicked.connect(self._set_thumbnail)
        self.button_discard_thumbnail.clicked.connect(
            lambda: self.line_edit_thumbnail.setText("")
        )
        self.button_capture_thumbnail.clicked.connect(self._capture_thumbnail)

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

            path_workfile = Path(hou.hipFile.basename())
            path_workfile_path = Path(hou.hipFile.path())
            self.workfile = str(path_workfile.as_posix())
            self.workfile_path = str(path_workfile_path.as_posix())
            self.line_edit_workfile.setText(self.workfile)
            self.line_edit_path.setText(self.workfile_path)
        except ImportError as exception:
            _logger.error(f"Error: {str(exception)}")

    def _get_current_workfile(self) -> None:
        """Get the current workfile."""

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

    def _build_save_path(self) -> None:
        """Build the save path for the workfile."""

        directory = Path(self.line_edit_path.text()).parent
        workfile = Path(self.line_edit_workfile.text())
        version = self.spinbox_version.value()

        # Workfile saved with fxquinox: "Research_Research_010_0010_v015.hip"
        # Other workfile: "untitled.hip"

        version_str = f"v{version:03d}"
        base_name = workfile.stem
        extension = workfile.suffix

        # Regular expression to find an existing version pattern (e.g., v001)
        version_pattern = re.compile(r"_v(\d{3})(\.\w+)?$")

        # Check if the base name ends with a version pattern
        if version_pattern.search(base_name):
            # Replace the existing version with the new version
            new_base_name = version_pattern.sub(f"_{version_str}", base_name)
        else:
            # Append the new version to the base name
            new_base_name = f"{base_name}_{version_str}"

        # Reconstruct the full path with the new base name and extension
        new_path = directory / f"{new_base_name}{extension}"
        self.line_edit_to_save.setText(new_path.as_posix())

        # WRONG: "C:/Users/valen/untitled.hip/v001"

    def _get_current_version(self) -> None:
        """Get the current version of the workfile."""

        workfile = self.line_edit_workfile.text()
        version = fxfiles.find_version_in_filename(workfile)

        if version:
            self.spinbox_version.setValue(version + 1)
        else:
            self.spinbox_version.setValue(1)

    def _set_thumbnail(self):
        """Choose a thumbnail for the shot."""

        # Get the path to the thumbnail
        thumbnail_path = QFileDialog.getOpenFileName(
            self,
            caption="Select Thumbnail",
            dir=QDir.homePath(),
            filter="Images (*.png *.jpg *.jpeg *.bmp *.gif)",
        )[0]

        if thumbnail_path:
            self.line_edit_thumbnail.setText(thumbnail_path)

    def _capture_thumbnail(self):
        """Capture a thumbnail for the current workfile."""

        self.screen_capture_window = FXScreenCaptureWindow(
            self,
            entity_name=Path(self.line_edit_to_save.text()).stem,
            entity_dir=Path(self.line_edit_to_save.text()).parent,
        )
        self.screen_capture_window.selection_complete.connect(
            lambda path: self._on_thumbnail_capture_complete(path)
        )
        self.screen_capture_window._exec()

    def _on_thumbnail_capture_complete(self, thumbnail_path: str):
        """Handle the completion of the thumbnail capture.

        Args:
            thumbnail_path (str): The path to the captured thumbnail.
        """

        self.line_edit_thumbnail.setText(thumbnail_path)

    def _preview_thumbnail(self):
        """Preview the thumbnail for the shot."""

        fxutils.open_directory(self.line_edit_thumbnail.text())

    def _set_workfile_metadata(
        self,
        file_name: str,
        file_path: str,
        file_dir: str,
        version: str,
        comment: str,
        thumbnail: str,
    ) -> None:
        """Set the metadata for the workfile.

        Args:
            file_name (str): The name of the workfile.
            file_path (str): The path to the workfile.
            file_dir (str): The directory of the workfile.
            version (str): The version of the workfile, e.g. "v001".
            comment (str): The comment for the workfile.
        """

        metadata = {
            "creator": "fxquinox",
            "entity": "workfile",
            "name": file_name,
            "path": file_path,
            "parent": file_dir,
            "description": "Workfile",
            "version": version,
            "comment": comment,
            "user": getpass.getuser(),
            "thumbnail": thumbnail,
        }
        fxfiles.set_multiple_metadata(file_path, metadata)

    def _save_workfile_houdini(self, file_path: str) -> None:
        """Opens the workfile in Houdini.

        Args:
            file_path (str): The path to the workfile.
        """

        try:
            import hou  # type: ignore

            hou.hipFile.save(file_path)
        except ImportError as exception:
            _logger.error(f"Error: {str(exception)}")

    def _save_workfile(self) -> None:
        """Save the workfile."""

        workfile_path = self.line_edit_to_save.text()
        workfile_name = Path(workfile_path).name
        workfile_dir = Path(workfile_path).parent.as_posix()
        workfile_version = f"v{self.spinbox_version.value():03d}"
        workfile_comment = self.text_edit_comment.toPlainText() or ""
        workfile_thumbnail = self.line_edit_thumbnail.text() or ""

        if self.dcc == fxentities.DCC.standalone:
            pass

        elif self.dcc == fxentities.DCC.blender:
            pass

        elif self.dcc == fxentities.DCC.houdini:
            self._save_workfile_houdini(workfile_path)
            self._set_workfile_metadata(
                file_name=workfile_name,
                file_path=workfile_path,
                file_dir=workfile_dir,
                version=workfile_version,
                comment=workfile_comment,
                thumbnail=workfile_thumbnail,
            )
            self.close()

        elif self.dcc == fxentities.DCC.maya:
            pass

        elif self.dcc == fxentities.DCC.nuke:
            pass

        elif self.dcc == fxentities.DCC.photoshop:
            pass


def run_save_workfile(
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
    run_save_workfile()
