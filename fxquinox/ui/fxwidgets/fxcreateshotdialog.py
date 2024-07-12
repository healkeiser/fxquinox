# Built-in
from pathlib import Path
from PIL import Image
import shutil

# Third-party
from fxgui import fxicons, fxutils as fxguiutils
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *

# Internal
from fxquinox import fxcore, fxenvironment, fxfiles, fxlog, fxutils


# Log
_logger = fxlog.get_logger("fxcreateshotdialog")
_logger.setLevel(fxlog.DEBUG)


class FXCreateShotDialog(QDialog):
    def __init__(
        self, parent=None, project_name=None, project_root=None, project_assets=None, project_shots=None, sequence=None
    ):
        super().__init__(parent)

        # Attributes
        self.project_name = project_name
        self._project_root = project_root
        self._project_assets_path = project_assets
        self._project_shots_path = project_shots
        self.sequence = sequence

        # Methods
        self.setModal(True)

        self._create_ui()
        self._rename_ui()
        self._modify_ui()
        self._handle_connections()
        self._populate_sequences()
        self._disable_ui()

        _logger.info("Initialized create shot")

    def _create_ui(self):
        """_summary_"""

        ui_file = Path(fxenvironment._FXQUINOX_UI) / "create_shot.ui"
        self.ui = fxguiutils.load_ui(self, str(ui_file))
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)
        self.setWindowTitle("Create Shot")

    def _rename_ui(self):
        """_summary_"""

        self.label_icon_sequence: QLabel = self.ui.label_icon_sequence
        self.combo_box_sequence: QComboBox = self.ui.combo_box_sequence
        self.label_icon_shot: QLabel = self.ui.label_icon_shot
        self.line_edit_shot: QLineEdit = self.ui.line_edit_shot
        self.label_icon_frame_range: QLabel = self.ui.label_icon_frame_range
        self.spin_box_cut_in: QSpinBox = self.ui.spin_box_cut_in
        self.spin_box_cut_out: QSpinBox = self.ui.spin_box_cut_out
        self.label_icon_thumbnail: QLabel = self.ui.label_icon_thumbnail
        self.line_edit_thumbnail: QLineEdit = self.ui.line_edit_thumbnail
        self.button_pick_thumbnail: QPushButton = self.ui.button_pick_thumbnail
        self.button_discard_thumbnail: QPushButton = self.ui.button_discard_thumbnail
        self.group_box_metadata: QGroupBox = self.ui.group_box_metadata
        self.button_add_metadata: QPushButton = self.ui.button_add_metadata
        self.frame_metadata: QFrame = self.ui.frame_metadata
        self.button_box: QDialogButtonBox = self.ui.button_box

    def _handle_connections(self):
        """_summary_"""

        self.button_add_metadata.clicked.connect(self._add_metadata_line)
        self.button_pick_thumbnail.clicked.connect(self._set_thumbnail)
        self.button_discard_thumbnail.clicked.connect(lambda: self.line_edit_thumbnail.clear())

    def _modify_ui(self):
        """_summary_"""

        # Set the regular expression validator for the sequence and shot inputs
        reg_exp = QRegExp("[A-Za-z0-9-_]+")
        validator = QRegExpValidator(reg_exp)

        self.label_icon_sequence.setPixmap(fxicons.get_pixmap("perm_media", 18))
        self.combo_box_sequence.setValidator(validator)
        self.label_icon_shot.setPixmap(fxicons.get_pixmap("image", 18))
        self.line_edit_shot.setValidator(validator)
        self.label_icon_frame_range.setPixmap(fxicons.get_pixmap("alarm", 18))
        self.label_icon_thumbnail.setPixmap(fxicons.get_pixmap("camera", 18))
        self.button_pick_thumbnail.setIcon(fxicons.get_icon("add_a_photo"))
        self.button_discard_thumbnail.setIcon(fxicons.get_icon("delete"))
        self.button_add_metadata.setIcon(fxicons.get_icon("add"))

        # Contains some slots connections, to avoid iterating multiple times
        # over the buttons
        for button in self.button_box.buttons():
            role = self.button_box.buttonRole(button)
            if role == QDialogButtonBox.AcceptRole:
                button.setIcon(fxicons.get_icon("check", color="#8fc550"))
                button.setText("Create")
                # Create shot
                button.clicked.connect(self._create_shot)
            elif role == QDialogButtonBox.RejectRole:
                button.setIcon(fxicons.get_icon("close", color="#ec0811"))
                # Close
                button.clicked.connect(self.close)
            elif role == QDialogButtonBox.ResetRole:
                button.setIcon(fxicons.get_icon("refresh"))
                # Reset connection
                button.clicked.connect(self._reset_ui_values)

    def _disable_ui(self):
        """Disable all sibling widgets of the current widget without disabling
        the current widget itself.
        """

        parent = self.parent()
        if not parent:
            return

    def _populate_sequences(self):
        """Populates the sequence combo box with the available sequences."""

        shots_dir = Path(self._project_root) / "production" / "shots"
        if not shots_dir.exists():
            return

        sequences = [sequence.name for sequence in shots_dir.iterdir() if sequence.is_dir()]
        self.combo_box_sequence.addItems(sequences)

        # Set the current sequence to the one passed as an argument if it exists
        if self.sequence:
            for index in range(self.combo_box_sequence.count()):
                if self.combo_box_sequence.itemText(index) == self.sequence:
                    self.combo_box_sequence.setCurrentIndex(index)
                    break

    def _set_thumbnail(self):
        """Choose a thumbnail for the shot."""

        config_file_name = "general.cfg"
        config_section_name = "project_browser_create_shot"
        config_option_name = "last_thumbnail_directory"

        previous_directory = (
            fxutils.get_configuration_file_value(config_file_name, config_section_name, config_option_name)
            or Path.home().resolve().as_posix()
        )

        # Get the path to the thumbnail
        thumbnail_path = QFileDialog.getOpenFileName(
            self, "Select Thumbnail", previous_directory, "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )[0]

        if thumbnail_path:
            self.line_edit_thumbnail.setText(thumbnail_path)

            # Update the config with the parent directory of the selected thumbnail
            fxutils.update_configuration_file(
                config_file_name,
                config_section_name,
                config_option_name,
                Path(thumbnail_path).parent.resolve().as_posix(),
            )

    def _add_metadata_line(self):
        """Adds a new line for entering metadata key-value pairs."""

        # Create widgets
        key_edit = QLineEdit()
        value_edit = QLineEdit()
        delete_button = QPushButton()
        delete_button.setIcon(fxicons.get_icon("delete"))
        key_edit.setPlaceholderText("Key...")
        value_edit.setPlaceholderText("Value...")

        # Set object names for later reference
        key_edit.setObjectName("line_edit_key_metadata")
        value_edit.setObjectName("line_edit_value_metadata")
        delete_button.setObjectName("button_delete_metadata")

        # Layout to hold the new line widgets
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(key_edit)
        layout.addWidget(value_edit)
        layout.addWidget(delete_button)

        # Container widget
        container = QWidget()
        container.setLayout(layout)

        # Add the container to your main layout
        layout_metadata = QVBoxLayout()
        layout_metadata.setContentsMargins(0, 0, 0, 0)
        self.frame_metadata.setLayout(layout_metadata)
        self.frame_metadata.layout().addWidget(container)

        # Connect the delete button's clicked signal
        delete_button.clicked.connect(lambda: self._delete_metadata_line(container))

    def _delete_metadata_line(self, container):
        """Deletes a specified metadata line."""

        # Remove the container from the layout and delete it
        self.group_box_metadata.layout().removeWidget(container)
        container.deleteLater()

    def _reset_ui_values(self):
        """Resets the values of all UI elements to their default states."""

        # Reset QLineEdit and QSpinBox widgets
        self.line_edit_shot.setText("")
        self.spin_box_cut_in.setValue(1001)
        self.spin_box_cut_out.setValue(1100)

        # Clear QComboBox selection
        self.combo_box_sequence.setCurrentIndex(0)

        # Remove all dynamically added metadata lines
        layout_metadata = self.frame_metadata.layout()
        if layout_metadata:
            while layout_metadata.count():
                item = layout_metadata.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

    def _create_shot(self):
        """Creates a shot based on the entered values."""

        # Get the values from the UI elements
        sequence = self.combo_box_sequence.currentText()
        shot = self.line_edit_shot.text()
        cut_in = self.spin_box_cut_in.value()
        cut_out = self.spin_box_cut_out.value()

        # Create the shot
        sequence_dir = Path(self._project_root) / "production" / "shots" / sequence

        # If sequence does not exist, create it
        if not sequence_dir.exists():
            fxcore.create_sequence(sequence, self._project_shots_path)

        shot_dir = sequence_dir / shot
        shot = fxcore.create_shot(shot, sequence_dir, self)
        if not shot:
            # self.close()
            return

        # Get the thumbnail path
        thumbnail_path = self.line_edit_thumbnail.text()
        if thumbnail_path and Path(thumbnail_path).is_file():

            old_thumbnail_path = Path(thumbnail_path)
            thumbnail_name = f"{shot}.jpg"
            thumbnail_dir = shot_dir / ".thumbnails"
            thumbnail_dir.mkdir(parents=True, exist_ok=True)
            new_thumbnail_path = thumbnail_dir / thumbnail_name
            shutil.copy(old_thumbnail_path, new_thumbnail_path)

            # Resize and convert the copied image to JPG
            target_width, target_height = 480, 270
            with Image.open(new_thumbnail_path) as img:
                # Calculate the scaling factor to ensure at least one side matches the target size
                scaling_factor = max(target_width / img.width, target_height / img.height)

                # Resize the image with the scaling factor
                new_size = (int(img.width * scaling_factor), int(img.height * scaling_factor))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

                # Calculate the cropping area
                left = (img.width - target_width) / 2
                top = (img.height - target_height) / 2
                right = (img.width + target_width) / 2
                bottom = (img.height + target_height) / 2

                # Crop the image to the target size
                img = img.crop((left, top, right, bottom))

                # Convert to RGB and save
                img.convert("RGB").save(new_thumbnail_path, "JPEG")

            shot_dir_str = str(shot_dir)
            fxfiles.set_metadata(shot_dir_str, "thumbnail", new_thumbnail_path.resolve().as_posix())

            _logger.debug(f"Thumbnail path: '{thumbnail_path}'")
            _logger.debug(f"Thumbnail dir: '{thumbnail_dir}'")

        # Get the metadata key-value pairs
        metadata = {}
        layout_metadata = self.frame_metadata.layout()

        if layout_metadata is not None:
            for i in range(layout_metadata.count()):
                item = layout_metadata.itemAt(i)
                if item.widget():
                    key = item.widget().findChild(QLineEdit, "line_edit_key_metadata").text()
                    value = item.widget().findChild(QLineEdit, "line_edit_value_metadata").text()
                    metadata[key] = value

        # Add cut in and cut out to the metadata dictionary
        metadata["cut_in"] = cut_in
        metadata["cut_out"] = cut_out

        # Add metadata to the shot folder
        if metadata:
            shot_dir_str = str(shot_dir)
            for key, value in metadata.items():
                if key and value:
                    _logger.debug(f"Adding metadata: '{key}' - '{value}'")
                    fxfiles.set_metadata(shot_dir_str, key, value)

        # Feedback
        parent = self.parent()
        if parent:
            parent.statusBar().showMessage(
                f"Created shot '{shot}' in sequence '{sequence}'", parent.SUCCESS, logger=_logger
            )

        # Refresh parent and close QDialog on completion
        parent = self.parent()
        if parent:
            parent.refresh()

        self.close()

    def closeEvent(self, _) -> None:
        """Overrides the close event."""

        _logger.info(f"Closed")
        self.setParent(None)


def run_create_shot():
    app = QApplication([])
    dialog = FXCreateShotDialog()
    dialog.show()
    app.exec_()


if __name__ == "__main__":
    run_create_shot()
