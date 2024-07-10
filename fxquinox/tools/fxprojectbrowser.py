# Built-in
from datetime import datetime
from functools import partial
import getpass
import os
from pathlib import Path
from PIL import Image
import shutil
from typing import Optional, Tuple

# Third-party
from fxgui import fxwidgets, fxicons, fxutils as fxguiutils
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *
import yaml

# Internal
from fxquinox import fxlog, fxfiles, fxutils, fxentities, fxcore


# Log
_logger = fxlog.get_logger("fxquinox.tools.fxprojectbrowser")
_logger.setLevel(fxlog.DEBUG)


class FXThumbnailItemDelegate(QStyledItemDelegate):
    # ! The `show_thumbnail` flag should be stored in the `Qt.UserRole + 1` as bool
    # ! The thumbnail path should be stored in the `Qt.UserRole + 2` as str

    def sizeHint(self, option, index):
        # Check if the thumbnail should be shown
        show_thumbnail = index.data(Qt.UserRole + 1)
        if show_thumbnail is None or show_thumbnail:  # Show thumbnail by default
            # Increase the height of the items for thumbnails
            original_size = super().sizeHint(option, index)
            return QSize(original_size.width(), 50)  # Increased item height for thumbnails
        else:
            # Return a smaller height if the thumbnail is disabled
            original_size = super().sizeHint(option, index)
            return QSize(original_size.width(), 20)  # Reduced item height without thumbnails

    def paint(self, painter, option, index):
        # Fill the entire item's background first
        background_color = (
            option.palette.window() if not (option.state & QStyle.State_Selected) else option.palette.highlight()
        )
        painter.fillRect(option.rect, background_color)
        if index.column() == 0:  # Check if it's the first column
            # Check if the thumbnail should be shown
            show_thumbnail = index.data(Qt.UserRole + 1)
            if show_thumbnail is None or show_thumbnail:  # Show thumbnail by default
                # Load the thumbnail
                thumbnail_path = index.data(Qt.UserRole + 2)
                if thumbnail_path:
                    thumbnail = QPixmap(thumbnail_path)
                else:
                    # Fallback path if no thumbnail path is set
                    thumbnail_path = Path(__file__).parents[1] / "images" / "missing_image.png"
                    thumbnail = QPixmap(thumbnail_path.resolve().as_posix())

                # Adjust the target height for scaling the thumbnail, subtracting 10 pixels for top and bottom spaces
                item_height = option.rect.height() - 10  # 5 pixels space on top and bottom
                thumbnail = thumbnail.scaledToHeight(item_height - 2, Qt.SmoothTransformation)  # Subtract border width

                # Create a new QPixmap for the border and rounded corners
                bordered_thumbnail = QPixmap(thumbnail.size() + QSize(2, 2))  # Add space for the border
                bordered_thumbnail.fill(Qt.transparent)  # Fill with transparent background

                # Use QPainter to draw the border and image with rounded corners
                painter_with_border = QPainter(bordered_thumbnail)
                painter_with_border.setRenderHint(QPainter.Antialiasing)
                painter_with_border.setPen(QPen(Qt.white, 1))  # White pen for the border
                painter_with_border.setBrush(QBrush(thumbnail))  # Use the thumbnail as the brush
                radius = 2  # Adjust radius
                painter_with_border.drawRoundedRect(
                    bordered_thumbnail.rect().marginsRemoved(QMargins(1, 1, 1, 1)), radius, radius
                )

                painter_with_border.end()  # Finish drawing

                # Adjust the y-coordinate to add a 5-pixel offset from the top
                x_offset = 5  # Offset from the left border of the item
                y_offset = 5  # Pixels space on top
                y = option.rect.top() + y_offset  # Align to the top of the item with a 5-pixel offset

                painter.drawPixmap(option.rect.left() + x_offset, y, bordered_thumbnail)

                # Adjust the option.rect for the icon and text to be on the right of the thumbnail
                thumbnail_width_with_padding = bordered_thumbnail.width() + x_offset * 2
            else:
                # If not showing thumbnail, adjust padding as if there's no thumbnail
                thumbnail_width_with_padding = 0

            new_option = QStyleOptionViewItem(option)
            new_option.rect = QRect(
                option.rect.left() + thumbnail_width_with_padding,
                option.rect.top(),
                option.rect.width() - thumbnail_width_with_padding,
                option.rect.height(),
            )

            # Call the base class paint method with the adjusted rect
            super().paint(painter, new_option, index)
        else:
            # For other columns, use the default painting
            super().paint(painter, option, index)


class FXProjectBrowserWindow(fxwidgets.FXMainWindow):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        icon: Optional[str] = None,
        title: Optional[str] = None,
        size: Optional[int] = None,
        documentation: Optional[str] = None,
        project: Optional[str] = None,
        version: Optional[str] = None,
        company: Optional[str] = None,
        color_a: Optional[str] = None,  # "#3c3c3c",  # "#4a4a4a",
        color_b: Optional[str] = None,  # "#656565",  # "#3e3e3e",
        ui_file: Optional[str] = None,
        dcc: fxentities.DCC = fxentities.DCC.standalone,
    ):
        super().__init__(
            parent,
            icon,
            title,
            size,
            documentation,
            project,
            version,
            company,
            color_a,
            color_b,
            ui_file,
        )

        # Attributes
        self.dcc = dcc

        self.asset = None
        self.sequence: str = None
        self.shot: str = None
        self.step: str = None
        self.task: str = None
        self.workfile: str = None

        # Methods
        self._get_project()
        self._rename_ui()
        self._create_icons()
        self._modify_ui()
        self._populate_assets()
        self._populate_shots()
        self._handle_connections()

        # self.status_line.hide()
        self.set_status_line_colors("#999999", "#656565")
        self.statusBar().showMessage("Initialized project browser", self.INFO, logger=_logger)

    def _get_project(self) -> None:
        """_summary_

        Returns:
            dict: _description_
        """

        self.project_info = fxcore.get_project()
        self._project_root = self.project_info.get("FXQUINOX_PROJECT_ROOT", None)
        self._project_name = self.project_info.get("FXQUINOX_PROJECT_NAME", None)
        self._project_assets = self.project_info.get("FXQUINOX_PROJECT_ASSETS", None)
        self._project_shots = self.project_info.get("FXQUINOX_PROJECT_SHOTS", None)

    def _rename_ui(self):
        """_summary_"""

        self.label_project: QLabel = self.ui.label_project
        self.line_project: QFrame = self.ui.line_project
        #
        self.tab_assets_shots: QTabWidget = self.ui.tab_assets_shots
        #
        self.tab_assets: QWidget = self.ui.tab_assets
        self.label_icon_filter_assets: QLabel = self.ui.label_icon_filter_assets
        self.line_edit_filter_assets: QLineEdit = self.ui.frame_filter_assets
        self.tree_widget_assets: QTreeWidget = self.ui.tree_widget_assets
        #
        self.tab_shots: QWidget = self.ui.tab_shots
        self.label_icon_filter_shots: QLabel = self.ui.label_icon_filter_shots
        self.line_edit_filter_shots: QLineEdit = self.ui.line_edit_filter_shots
        self.tree_widget_shots: QTreeWidget = self.ui.tree_widget_shots
        #
        self.group_box_steps: QGroupBox = self.ui.group_box_steps
        self.list_steps: QListWidget = self.ui.list_steps
        #
        self.group_box_tasks: QGroupBox = self.ui.group_box_tasks
        self.list_tasks: QListWidget = self.ui.list_tasks
        #
        self.checkbox_display_latest_worfiles: QCheckBox = self.ui.checkbox_display_latest_worfiles
        self.label_icon_filter_workfiles: QLabel = self.ui.label_icon_filter_workfiles
        self.combobox_filter_workfiles: QComboBox = self.ui.combobox_filter_workfiles
        self.tree_widget_workfiles: QTreeWidget = self.ui.tree_widget_workfiles
        #
        self.group_box_info: QGroupBox = self.ui.group_box_info

    def _handle_connections(self):
        # Assets
        self.tree_widget_assets.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget_assets.customContextMenuRequested.connect(self._on_assets_context_menu)
        self.tree_widget_assets.itemSelectionChanged.connect(self._get_current_asset)
        self.tree_widget_assets.itemSelectionChanged.connect(lambda: self._display_metadata(fxentities.entity.asset))

        # Shots
        self.tree_widget_shots.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget_shots.customContextMenuRequested.connect(self._on_shots_context_menu)
        self.tree_widget_shots.itemSelectionChanged.connect(self._get_current_sequence_and_shot)
        self.tree_widget_shots.itemSelectionChanged.connect(self._populate_steps)
        self.tree_widget_shots.itemSelectionChanged.connect(self._handle_sequence_shot_selection)

        self.line_edit_filter_shots.textChanged.connect(
            lambda: fxguiutils.filter_tree(self.line_edit_filter_shots, self.tree_widget_shots, 0)
        )

        # Steps
        self.list_steps.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_steps.customContextMenuRequested.connect(self._on_steps_context_menu)
        self.list_steps.itemSelectionChanged.connect(self._get_current_step)
        self.list_steps.itemSelectionChanged.connect(self._populate_tasks)
        self.list_steps.itemSelectionChanged.connect(lambda: self._display_metadata(fxentities.entity.step))

        # Tasks
        self.list_tasks.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_tasks.customContextMenuRequested.connect(self._on_tasks_context_menu)
        self.list_tasks.itemSelectionChanged.connect(self._get_current_task)
        self.list_tasks.itemSelectionChanged.connect(self._populate_workfiles)
        self.list_tasks.itemSelectionChanged.connect(lambda: self._display_metadata(fxentities.entity.task))

        # Workfiles
        self.checkbox_display_latest_worfiles.stateChanged.connect(self._on_show_latest_workfile_changed)
        self.combobox_filter_workfiles.currentIndexChanged.connect(self._on_filter_workfiles_by_type_changed)
        self.combobox_filter_workfiles.currentIndexChanged.connect(self._populate_workfiles)
        self.tree_widget_workfiles.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget_workfiles.customContextMenuRequested.connect(self._on_workfiles_context_menu)
        self.tree_widget_workfiles.itemSelectionChanged.connect(self._get_current_workfile)
        self.tree_widget_workfiles.itemSelectionChanged.connect(
            lambda: self._display_metadata(fxentities.entity.workfile)
        )
        self.tree_widget_workfiles.doubleClicked.connect(self._open_workfile)

        #
        self.refresh_action.triggered.connect(self.refresh)

    def _handle_sequence_shot_selection(self):
        selected_items = self.tree_widget_shots.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        item_type = item.data(0, Qt.UserRole)

        _logger.debug(f"Item type: '{item_type}'")

        if item_type == "shot":
            self._display_metadata(fxentities.entity.shot)
        elif item_type == "sequence":
            self._display_metadata(fxentities.entity.sequence)
        else:
            return

    def _create_icons(self):
        """_summary_"""

        self.icon_search = fxicons.get_pixmap("search", 18)
        self.icon_filter = fxicons.get_pixmap("filter_alt", 18)

    def _modify_ui(self):
        """Modifies the UI elements."""

        # Labels
        font_bold = QFont()
        font_bold.setBold(True)
        self.label_project.setText(self._project_name)
        self.label_project.setFont(font_bold)

        # Icons
        self.tab_assets_shots.setTabIcon(0, fxicons.get_icon("view_in_ar"))
        self.tab_assets_shots.setTabIcon(1, fxicons.get_icon("image"))
        self.label_icon_filter_assets.setPixmap(self.icon_search)
        self.label_icon_filter_shots.setPixmap(self.icon_search)
        self.label_icon_filter_workfiles.setPixmap(self.icon_filter)

        # Shots
        header_item = QTreeWidgetItem(["Shots"])
        self.tree_widget_shots.setHeaderItem(header_item)
        header_item.setIcon(0, fxicons.get_icon("image"))
        # self.tree_widget_shots.setIconSize(QSize(18, 18))

        # Steps
        # self.list_steps.setIconSize(QSize(18, 18))

        # Tasks
        # self.list_tasks.setIconSize(QSize(18, 18))

        # Assets
        header_item = QTreeWidgetItem(["Assets"])
        self.tree_widget_assets.setHeaderItem(header_item)
        header_item.setIcon(0, fxicons.get_icon("view_in_ar"))
        self.tree_widget_assets.setIconSize(QSize(18, 18))

        # Workfiles
        self.checkbox_display_latest_worfiles.setVisible(False)
        header_item = QTreeWidgetItem(
            ["Workfiles", "Version", "Comment", "Date Created", "Date Modified", "User", "Size"]
        )
        self.tree_widget_workfiles.setHeaderItem(header_item)
        header_item.setIcon(0, fxicons.get_icon("description"))
        header_item.setIcon(1, fxicons.get_icon("tag"))
        header_item.setIcon(2, fxicons.get_icon("comment"))
        header_item.setIcon(3, fxicons.get_icon("schedule"))
        header_item.setIcon(4, fxicons.get_icon("update"))
        header_item.setIcon(5, fxicons.get_icon("person"))
        header_item.setIcon(6, fxicons.get_icon("scale"))
        self.tree_widget_workfiles.setIconSize(QSize(18, 18))

    #
    def refresh(self):
        # Display statusbar message and change icon
        # self.statusBar().showMessage("Refreshing...", fxwidgets.INFO, logger=_logger)

        # Methods to run
        self._populate_assets()
        self._populate_shots()
        self._populate_steps()
        self._populate_tasks()
        self._populate_workfiles()

    # ' Populating methods
    # Shots
    def _populate_shots(self) -> None:
        """Populates the shots tree widget with the shots in the project."""

        # Delegate
        self.tree_widget_shots.setItemDelegate(FXThumbnailItemDelegate())
        # ! Set thumbnail by using the `Qt.UserRole + 2` role

        # Store the states (expanded and selected items)
        expanded_states = self._store_expanded_states(self.tree_widget_shots)
        selected_states = self._store_selection_state_tree(self.tree_widget_shots)

        # Clear
        self.tree_widget_shots.clear()

        # Check if the project root is set
        if not self._project_root:
            return

        # Check if the shots directory exists
        shots_dir = Path(self._project_root) / "production" / "shots"
        if not shots_dir.exists():
            return

        # Iterate over the sequences and shots
        icon_sequence = fxicons.get_pixmap("perm_media")
        icon_shot = fxicons.get_pixmap("image")
        font_bold = QFont()
        font_bold.setBold(True)

        for sequence in shots_dir.iterdir():
            if not sequence.is_dir():
                continue

            sequence_item = QTreeWidgetItem(self.tree_widget_shots)
            sequence_item.setText(0, sequence.name)
            sequence_item.setIcon(0, icon_sequence)
            sequence_item.setFont(0, font_bold)
            sequence_path = sequence.resolve().absolute().as_posix()
            # Set data
            sequence_item.setData(0, Qt.UserRole, fxentities.entity.sequence)
            sequence_item.setData(1, Qt.UserRole, sequence_path)
            sequence_item.setData(0, Qt.UserRole + 1, False)  # Disable thumbnail for sequence

            sequence_item.setToolTip(
                0,
                f"<b>{sequence.name}</b><hr><b>Entity</b>: Sequence<br><br><b>Path</b>: {sequence_path}",
            )

            # Check if the sequence has shots
            for shot in sequence.iterdir():
                if not shot.is_dir():
                    continue

                shot_item = QTreeWidgetItem(sequence_item)
                shot_item.setText(0, shot.name)
                shot_item.setIcon(0, icon_shot)
                shot_path = shot.resolve().absolute().as_posix()

                # Set data
                shot_item.setData(0, Qt.UserRole, fxentities.entity.shot)
                shot_item.setData(1, Qt.UserRole, shot_path)
                shot_item.setData(0, Qt.UserRole + 1, True)  # Enable thumbnail for shot
                # Set thumbnail
                thumbnail_path = fxfiles.get_metadata(shot_path, "thumbnail")
                if thumbnail_path:
                    shot_item.setData(0, Qt.UserRole + 2, thumbnail_path)

                # Set tooltip
                shot_item.setToolTip(
                    0,
                    f"<b>{shot.name}</b><hr><b>Entity</b>: Shot<br><br><b>Path</b>: {shot_path}",
                )

        # Restore states
        self._restore_expanded_states(self.tree_widget_shots, expanded_states)
        self._restore_selection_state_tree(self.tree_widget_shots, selected_states)

        # After populating the tree, select the first item if it exists
        # self._select_first_item_in_tree(self.tree_widget_shots)

    def _get_current_sequence_and_shot(self) -> Tuple[str, str]:
        """Returns the current sequence and shot selected in the tree widget.
        Also sets the environment variables for the sequence and shot.

        Returns:
            Tuple[str, str]: A tuple containing the sequence and shot names.
        """

        current_item = self.tree_widget_shots.currentItem()
        if current_item is None:
            return None, None  # No item is selected

        parent_item = current_item.parent()
        # If no parent...
        if parent_item is None:
            # ...the current item is a sequence
            sequence = current_item
            shot = None
        else:
            # If parent, the current item is a shot, and its parent is
            # the sequence
            sequence = parent_item
            shot = current_item

        self.asset = None
        self.sequence = sequence.text(0) if sequence else None
        self.shot = shot.text(0) if shot else None
        os.environ["FXQUINOX_ASSET"] = ""
        os.environ["FXQUINOX_SEQUENCE"] = self.sequence if self.sequence else ""
        os.environ["FXQUINOX_SHOT"] = self.shot if self.shot else ""

        os.environ["FXQUINOX_ASSET_PATH"] = ""
        os.environ["FXQUINOX_SEQUENCE_PATH"] = sequence.data(1, Qt.UserRole) if sequence else ""
        os.environ["FXQUINOX_SHOT_PATH"] = shot.data(1, Qt.UserRole) if shot else ""

        _logger.debug(f"Asset: '{self.asset}', sequence: '{self.sequence}', shot: '{self.shot}'")

        return self.sequence, self.shot

    # Assets
    def _populate_assets(self) -> None:
        """Populates the assets tree widget with the assets in the project."""

        # Clear
        self.tree_widget_assets.clear()

        # Check if the assets directory exists
        assets_dir = Path(self._project_root) / "production" / "assets"
        if not assets_dir.exists():
            return

        # Delegate
        self.tree_widget_assets.setItemDelegate(FXThumbnailItemDelegate())
        # ! Set thumbnail by using the `Qt.UserRole + 1` role

        # Iterate over the assets
        icon_asset = fxicons.get_icon("view_in_ar")

        for asset in assets_dir.iterdir():
            if not asset.is_dir():
                continue

            asset_item = QTreeWidgetItem(self.tree_widget_assets)
            asset_item.setText(0, asset.name)
            asset_item.setIcon(0, icon_asset)

    def _get_current_asset(self) -> str:
        """Returns the current asset selected in the tree widget. Also sets the
        environment variables for the asset.

        Returns:
            str: The name of the asset.
        """

        current_item = self.tree_widget_assets.currentItem()
        if current_item is None:
            return None

        self.asset = current_item.text(0)
        self.sequence = None
        self.shot = None
        os.environ["FXQUINOX_ASSET"] = self.asset if self.asset else ""
        os.environ["FXQUINOX_SEQUENCE"] = ""
        os.environ["FXQUINOX_SHOT"] = ""

        os.environ["FXQUINOX_ASSET_PATH"] = current_item.data(1, Qt.UserRole) if current_item else ""
        os.environ["FXQUINOX_SEQUENCE_PATH"] = ""
        os.environ["FXQUINOX_SHOT_PATH"] = ""

        _logger.debug(f"Asset: '{self.asset}', sequence: '{self.sequence}', shot: '{self.shot}'")

        return self.asset

    # Steps
    def _populate_steps(self):
        # Clear
        self.list_steps.clear()

        # Check if the sequence and shot are set
        if self.sequence is None or self.shot is None:
            return

        # Check if the steps directory exists
        workfiles_dir = Path(self._project_root) / "production" / "shots" / self.sequence / self.shot / "workfiles"
        if not workfiles_dir.exists():
            return

        # Get the steps data for color and icon
        steps_file = Path(self._project_root) / ".pipeline" / "project_config" / "steps.yaml"
        if not steps_file.exists():
            return

        steps_data = yaml.safe_load(steps_file.read_text())

        # Iterate over the steps
        for step in workfiles_dir.iterdir():
            if not step.is_dir():
                continue

            step_name = step.name
            step_item = QListWidgetItem(step_name)

            # Find the matching step in steps_data based on step_name
            matching_step = next(
                (_step for _step in steps_data["steps"] if _step.get("name_long", None) == step_name), None
            )

            if matching_step:
                # Set the icon for the matching step
                step_item.setIcon(
                    fxicons.get_icon(
                        matching_step.get("icon", "check_box_outline_blank"),
                        color=matching_step.get("color", "#ffffff"),
                    )
                )
            else:
                # Set a default icon if no matching step is found
                step_item.setIcon(fxicons.get_icon("check_box_outline_blank"))

            step_path = step.resolve().absolute().as_posix()
            # Set data
            step_item.setData(Qt.UserRole, fxentities.entity.step)
            step_item.setData(Qt.UserRole + 1, step_path)
            step_item.setToolTip(f"<b>{step.name}</b><hr><b>Entity</b>: Step<br><br><b>Path</b>: {step_path}")
            self.list_steps.addItem(step_item)

        # After populating the list, select the first item if it exists
        self._select_first_item_in_list(self.list_steps)

    def _get_current_step(self) -> str:
        """Returns the current step selected in the list widget.

        Returns:
            str: The name of the step.
        """

        current_item = self.list_steps.currentItem()
        if current_item is None:
            return None

        self.step = current_item.text()

        os.environ["FXQUINOX_STEP"] = self.step if self.step else ""
        os.environ["FXQUINOX_STEP_PATH"] = current_item.data(Qt.UserRole + 1) if current_item else ""
        _logger.debug(f"Step: '{self.step}'")

        return self.step

    # Tasks
    def _populate_tasks(self):
        # Clear
        self.list_tasks.clear()

        # Check if the sequence, shot, and step are set
        if self.sequence is None or self.shot is None or self.step is None:
            return

        # Check if the tasks directory exists
        tasks_dir = (
            Path(self._project_root) / "production" / "shots" / self.sequence / self.shot / "workfiles" / self.step
        )
        if not tasks_dir.exists():
            return

        # Iterate over the tasks
        for task in tasks_dir.iterdir():
            if not task.is_dir():
                continue

            task_name = task.name
            task_item = QListWidgetItem(task_name)
            task_item.setIcon(fxicons.get_icon("task_alt"))
            task_path = task.resolve().absolute().as_posix()
            # Set data
            task_item.setData(Qt.UserRole, fxentities.entity.task)
            task_item.setData(Qt.UserRole + 1, task_path)
            task_item.setToolTip(f"<b>{task.name}</b><hr><b>Entity</b>: Task<br><br><b>Path</b>: {task_path}")
            self.list_tasks.addItem(task_item)

        # After populating the list, select the first item if it exists
        # self._select_first_item_in_list(self.list_tasks)

    def _get_current_task(self) -> str:
        """Returns the current task selected in the list widget.

        Returns:
            str: The name of the task.
        """

        current_item = self.list_tasks.currentItem()
        if current_item is None:
            return None

        self.task = current_item.text()
        os.environ["FXQUINOX_TASK"] = self.task if self.task else ""
        os.environ["FXQUINOX_TASK_PATH"] = current_item.data(Qt.UserRole + 1) if current_item else ""

        _logger.debug(f"Task: '{self.task}'")

        return self.task

    # Workfiles
    def _populate_workfiles(self):
        # Clear
        self.tree_widget_workfiles.clear()

        # Check if the sequence, shot, step, and task are set
        if self.sequence is None or self.shot is None or self.step is None or self.task is None:
            return

        # Check if the workfiles directory exists
        workfiles_dir = (
            Path(self._project_root)
            / "production"
            / "shots"
            / self.sequence
            / self.shot
            / "workfiles"
            / self.step
            / self.task
        )
        if not workfiles_dir.exists():
            return

        # Delegate
        self.tree_widget_workfiles.setItemDelegate(FXThumbnailItemDelegate())
        # ! Set thumbnail by using the `Qt.UserRole + 1` role

        # Font
        font_bold = QFont()
        font_bold.setBold(True)
        font_italic = QFont()
        font_italic.setItalic(True)

        def format_size(bytes, units=["bytes", "KB", "MB", "GB", "TB", "PB", "EB"]) -> str:
            """Simple helper to format bytes as a human-readable string.

            Args:
                bytes (int): The number of bytes to format.
                units (list, optional): The list of units to use.
                    Defaults to ["bytes", "KB", "MB", "GB", "TB", "PB", "EB"].

            Returns:
                str: The formatted string.
            """

            for unit in units:
                if bytes < 1024:
                    return f"{bytes:.2f} {unit}"
                bytes /= 1024

        # Iterate over the workfiles
        for workfile in workfiles_dir.iterdir():
            if not workfile.is_file():
                continue

            # Populate workfiles based on the selected workfile type in the combobox
            workfile_type = self.combobox_filter_workfiles.currentText()
            if workfile_type != "All":
                if workfile_type == "Blender" and not workfile.suffix.lstrip(".") in ["blend"]:
                    continue
                elif workfile_type == "Houdini" and not workfile.suffix.lstrip(".") in ["hip", "hipnc", "hiplc"]:
                    continue
                elif workfile_type == "Maya" and not workfile.suffix.lstrip(".") in ["ma", "mb"]:
                    continue
                elif workfile_type == "Nuke" and not workfile.suffix.lstrip(".") in ["nk"]:
                    continue
                elif workfile_type == "Photoshop" and not workfile.suffix.lstrip(".") in ["psd"]:
                    continue
                elif workfile_type == "Substance Painter" and not workfile.suffix.lstrip(".") in ["spp"]:
                    continue

            workfile_name = workfile.name
            workfile_type = workfile.suffix.lstrip(".")
            workfile_item = QTreeWidgetItem(self.tree_widget_workfiles)
            workfile_item.setText(0, workfile_name)
            workfile_path = workfile.resolve().absolute().as_posix()

            # Workfile
            workfile_item.setIcon(0, self._get_icon_based_on_type(workfile_type))
            workfile_item.setFont(0, font_bold)

            # Version
            workfile_item.setText(1, fxfiles.get_metadata(workfile_path, "version"))

            # Comment
            workfile_item.setText(2, fxfiles.get_metadata(workfile_path, "comment"))
            workfile_item.setFont(2, font_italic)

            # Date Created
            timestamp = workfile.stat().st_ctime
            readable_date = datetime.fromtimestamp(timestamp)
            formatted_date = readable_date.strftime("%Y/%m/%d %H:%M")
            workfile_item.setText(3, formatted_date)

            # Date Modified
            timestamp = workfile.stat().st_mtime
            readable_date = datetime.fromtimestamp(timestamp)
            formatted_date = readable_date.strftime("%Y/%m/%d %H:%M")
            workfile_item.setText(4, formatted_date)

            # User
            workfile_item.setText(5, fxfiles.get_metadata(workfile_path, "user"))

            # File size
            workfile_item.setText(6, format_size(workfile.stat().st_size))

            # Set data
            workfile_item.setData(0, Qt.UserRole, fxentities.entity.workfile)
            workfile_item.setData(1, Qt.UserRole, workfile_path)

            # Set tooltip
            workfile_item.setToolTip(
                0, f"<b>{workfile_name}</b><hr><b>Entity</b>: Workfile<br><br><b>Path</b>: {workfile_path}"
            )

        extra_space = 5
        for column_index in range(7):
            self.tree_widget_workfiles.resizeColumnToContents(column_index)
            current_width = self.tree_widget_workfiles.columnWidth(column_index)
            self.tree_widget_workfiles.setColumnWidth(column_index, current_width + extra_space)

        # After populating the tree, select the first item if it exists
        # self._select_first_item_in_tree(self.tree_widget_workfiles)

    def _toggle_latest_workfile_visibility(self, show_highest_only):
        if show_highest_only:
            highest_version = -1
            highest_version_item = None

            # Find the item with the highest version
            for i in range(self.tree_widget_workfiles.topLevelItemCount()):
                item = self.tree_widget_workfiles.topLevelItem(i)
                version_str = item.text(1)  # e.g., "v001"
                if len(version_str) > 1 and version_str[1:].isdigit():
                    version_num = int(version_str[1:])  # Convert to int
                else:
                    continue  # Skip items that don't have a valid version format

                if version_num > highest_version:
                    highest_version = version_num
                    highest_version_item = item

            # Hide all items except the one with the highest version
            for i in range(self.tree_widget_workfiles.topLevelItemCount()):
                item = self.tree_widget_workfiles.topLevelItem(i)
                item.setHidden(item != highest_version_item)
        else:
            # Show all items
            for i in range(self.tree_widget_workfiles.topLevelItemCount()):
                item = self.tree_widget_workfiles.topLevelItem(i)
                item.setHidden(False)

    def _on_show_latest_workfile_changed(self, state):
        show_highest_only = state == Qt.Checked
        self._toggle_latest_workfile_visibility(show_highest_only)

    def _filter_workfiles_by_type(self, workfile_type):
        if workfile_type == "All":
            for i in range(self.tree_widget_workfiles.topLevelItemCount()):
                item = self.tree_widget_workfiles.topLevelItem(i)
                item.setHidden(False)

        elif workfile_type == "Blender":
            for i in range(self.tree_widget_workfiles.topLevelItemCount()):
                item = self.tree_widget_workfiles.topLevelItem(i)
                if item.data(1, Qt.UserRole).endswith(".blend"):
                    item.setHidden(False)
                else:
                    item.setHidden(True)

        elif workfile_type == "Houdini":
            for i in range(self.tree_widget_workfiles.topLevelItemCount()):
                item = self.tree_widget_workfiles.topLevelItem(i)
                if (
                    item.data(1, Qt.UserRole).endswith(".hip")
                    or item.data(1, Qt.UserRole).endswith(".hipnc")
                    or item.data(1, Qt.UserRole).endswith(".hiplc")
                ):
                    item.setHidden(False)
                else:
                    item.setHidden(True)

        elif workfile_type == "Maya":
            for i in range(self.tree_widget_workfiles.topLevelItemCount()):
                item = self.tree_widget_workfiles.topLevelItem(i)
                if item.data(1, Qt.UserRole).endswith(".ma") or item.data(1, Qt.UserRole).endswith(".mb"):
                    item.setHidden(False)
                else:
                    item.setHidden(True)

        elif workfile_type == "Nuke":
            for i in range(self.tree_widget_workfiles.topLevelItemCount()):
                item = self.tree_widget_workfiles.topLevelItem(i)
                if item.data(1, Qt.UserRole).endswith(".nk") or item.data(1, Qt.UserRole).endswith(".nknc"):
                    item.setHidden(False)
                else:
                    item.setHidden(True)

        elif workfile_type == "Photoshop":
            for i in range(self.tree_widget_workfiles.topLevelItemCount()):
                item = self.tree_widget_workfiles.topLevelItem(i)
                if item.data(1, Qt.UserRole).endswith(".psd"):
                    item.setHidden(False)
                else:
                    item.setHidden(True)

        elif workfile_type == "Substance Painter":
            for i in range(self.tree_widget_workfiles.topLevelItemCount()):
                item = self.tree_widget_workfiles.topLevelItem(i)
                if item.data(1, Qt.UserRole).endswith(".spp"):
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    def _on_filter_workfiles_by_type_changed(self):
        workfile_type = self.combobox_filter_workfiles.currentText()
        if workfile_type != "All":
            self.label_icon_filter_workfiles.setPixmap(fxicons.get_pixmap("filter_alt", 18, color="#ffc107"))
        else:
            self.label_icon_filter_workfiles.setPixmap(self.icon_filter)

    def _get_current_workfile(self) -> str:
        """Returns the current workfile selected in the tree widget.

        Returns:
            str: The name of the workfile.
        """

        current_item = self.tree_widget_workfiles.currentItem()
        if current_item is None:
            return None

        self.workfile = current_item.text(0)
        os.environ["FXQUINOX_WORKFILE"] = self.workfile if self.workfile else ""
        os.environ["FXQUINOX_WORKFILE_PATH"] = current_item.data(1, Qt.UserRole) if current_item else ""

        _logger.debug(f"Workfile: '{self.workfile}'")

        return self.workfile

    # ? Define functions for each DCC opening
    def _open_workfile_standalone(self, file_path: str) -> None:
        self.open_file_or_folder(path=file_path)

    def _open_workfile_houdini(self, file_path: str) -> None:
        import hou

        if not self.parent() == hou.qt.mainWindow() or not hou:
            return

        # Load the Houdini file
        hou.hipFile.load(file_path)

        # Minimize the window after opening the file
        self.showMinimized()

    def _open_workfile(self):
        # TODO: Implement the open workfile method, using the defined executables in the launcher
        item = self.tree_widget_workfiles.currentItem()
        if item is None:
            return

        workfile_path = item.data(1, Qt.UserRole)

        if not Path(workfile_path).is_file():
            return

        if self.dcc == fxentities.DCC.standalone:
            self._open_workfile_standalone(workfile_path)

        elif self.dcc == fxentities.DCC.houdini:
            self._open_workfile_houdini(workfile_path)

        else:
            return

    def _get_icon_based_on_type(self, item_type: str) -> QIcon:
        """Returns an icon based on the item type.

        Args:
            item_type (str): The item type.

        Returns:
            QIcon: The icon.
        """

        path_icons_apps = Path(__file__).parents[1] / "images" / "icons" / "apps"

        if item_type in ["hip", "hipnc", "hiplc"]:
            icon = path_icons_apps / "houdini.svg"
            icon = QIcon(icon.resolve().as_posix())
        elif item_type in ["ma", "mb"]:
            icon = path_icons_apps / "maya.svg"
            icon = QIcon(icon.resolve().as_posix())
        elif item_type in ["nk", "nknc"]:
            icon = path_icons_apps / "nuke.svg"
            icon = QIcon(icon.resolve().as_posix())
        elif item_type in ["blend"]:
            icon = path_icons_apps / "blender.svg"
            icon = QIcon(icon.resolve().as_posix())
        elif item_type in ["max"]:
            icon = path_icons_apps / "3ds_max.svg"
            icon = QIcon(icon.resolve().as_posix())
        elif item_type in ["psd"]:
            icon = path_icons_apps / "photoshop.svg"
            icon = QIcon(icon.resolve().as_posix())
        elif item_type in ["ae"]:
            icon = path_icons_apps / "after_effects.svg"
            icon = QIcon(icon.resolve().as_posix())
        elif item_type in ["spp"]:
            icon = path_icons_apps / "substance_painter.svg"
            icon = QIcon(icon.resolve().as_posix())
        else:
            icon = fxicons.get_icon("description")

        return icon

    # Common
    def _select_first_item_in_tree(self, tree_widget: QTreeWidget):
        """Selects the first item in the tree widget.

        Args:
            tree_widget (QTreeWidget): The tree widget.
        """

        if tree_widget.topLevelItemCount() > 0:
            tree_widget.clearSelection()
            first_item = tree_widget.topLevelItem(0)
            tree_widget.setSelectionMode(QAbstractItemView.SingleSelection)
            first_item.setSelected(True)
            tree_widget.scrollToItem(first_item)

    def _select_first_item_in_list(self, list_widget: QListWidget):
        """Selects the first item in the list widget.

        Args:
            list_widget (QListWidget): The list widget.
        """

        if list_widget.count() > 0:
            list_widget.clearSelection()
            first_item = list_widget.item(0)
            list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
            first_item.setSelected(True)

    # States for QTreeWidget expansion
    def _store_expanded_states(self, tree_widget: QTreeWidget) -> dict:
        """Stores the expanded states of the tree widget items.

        Args:
            tree_widget (QTreeWidget): The tree widget to store the expanded
                states.

        Returns:
            dict: A dictionary containing the expanded states of the items.
        """

        expanded_states = {}
        for i in range(tree_widget.topLevelItemCount()):
            item = tree_widget.topLevelItem(i)
            self._store_item_state(item, expanded_states)
        return expanded_states

    def _store_item_state(self, item: QTreeWidgetItem, states: dict):
        """Stores the expanded state of the item and its children.

        Args:
            item (QTreeWidgetItem): The item to store the state.
            states (dict): The dictionary to store the states.
        """

        # ! Need each item to have a unique identifier in its text or via data
        identifier = item.text(0)  # or `item.data(0, Qt.UserRole)`
        states[identifier] = item.isExpanded()
        for i in range(item.childCount()):
            self._store_item_state(item.child(i), states)

    def _restore_expanded_states(self, tree_widget: QTreeWidget, states: dict):
        """Restores the expanded states of the tree widget items.

        Args:
            tree_widget (QTreeWidget): The tree widget to restore the expanded
                states.
            states (dict): The dictionary containing the expanded states of the
                items.
        """

        for i in range(tree_widget.topLevelItemCount()):
            item = tree_widget.topLevelItem(i)
            self._restore_item_state(item, states)

    def _restore_item_state(self, item: QTreeWidgetItem, states: dict):
        """Restores the expanded state of the item and its children.

        Args:
            item (QTreeWidgetItem): The item to restore the state.
            states (dict): The dictionary containing the states.
        """

        identifier = item.text(0)  # or `item.data(0, Qt.UserRole)`
        if identifier in states:
            item.setExpanded(states[identifier])
        for i in range(item.childCount()):
            self._restore_item_state(item.child(i), states)

    # States for QTreeWidget/QListWidget selections
    def _store_selection_state_tree(self, tree_widget: QTreeWidget) -> dict:
        """Stores the selection state of the tree widget items.

        Args:
            tree_widget (QTreeWidget): The tree widget to store the selection states.

        Returns:
            dict: A dictionary containing the selection states of the items.
        """
        selection_states = {}
        for i in range(tree_widget.topLevelItemCount()):
            item = tree_widget.topLevelItem(i)
            self._store_item_selection_state(item, selection_states)
        return selection_states

    def _store_item_selection_state(self, item: QTreeWidgetItem, states: dict):
        """Stores the selection state of the item and its children.

        Args:
            item (QTreeWidgetItem): The item to store the state.
            states (dict): The dictionary to store the states.
        """
        identifier = item.text(0)  # Assuming the first column text as a unique identifier
        states[identifier] = item.isSelected()
        for i in range(item.childCount()):
            child = item.child(i)
            self._store_item_selection_state(child, states)

    def _restore_selection_state_tree(self, tree_widget: QTreeWidget, states: dict):
        """Restores the selection states of the tree widget items.

        Args:
            tree_widget (QTreeWidget): The tree widget to restore the selection states.
            states (dict): The dictionary containing the selection states of the items.
        """
        for i in range(tree_widget.topLevelItemCount()):
            item = tree_widget.topLevelItem(i)
            self._restore_item_selection_state(item, states)

    def _restore_item_selection_state(self, item: QTreeWidgetItem, states: dict):
        """Restores the selection state of the item and its children.

        Args:
            item (QTreeWidgetItem): The item to restore the state.
            states (dict): The dictionary containing the states.
        """
        identifier = item.text(0)  # Assuming the first column text as a unique identifier
        if identifier in states:
            item.setSelected(states[identifier])
        for i in range(item.childCount()):
            child = item.child(i)
            self._restore_item_selection_state(child, states)

    def _store_selection_state_list(self, list_widget: QListWidget) -> list:
        """Stores the selection state of the list widget items.

        Args:
            list_widget (QListWidget): The list widget to store the selection states.

        Returns:
            list: A list indicating the selection state of each item.
        """
        selection_states = [item.isSelected() for item in range(list_widget.count())]
        return selection_states

    def _restore_selection_state_list(self, list_widget: QListWidget, states: list):
        """Restores the selection states of the list widget items.

        Args:
            list_widget (QListWidget): The list widget to restore the selection states.
            states (list): The list containing the selection states of the items.
        """
        for index, state in enumerate(states):
            item = list_widget.item(index)
            item.setSelected(state)

    # ' Metadata
    def _display_metadata(self, entity_type: str = None) -> None:
        """Displays the entity metadata in the group box info using a
        QTableWidget.

        Args:
            path (str): The path to the entity directory.
            entity_type (str): The entity type.
        """

        # Check if the directory exists
        if entity_type == fxentities.entity.sequence and self.sequence:
            path = Path(self._project_root) / "production" / "shots" / self.sequence
        elif entity_type == fxentities.entity.shot and self.sequence and self.shot:
            path = Path(self._project_root) / "production" / "shots" / self.sequence / self.shot
        elif entity_type == fxentities.entity.asset and self.asset:
            path = Path(self._project_root) / "production" / "assets" / self.asset
        elif entity_type == fxentities.entity.step and self.sequence and self.shot and self.step:
            path = (
                Path(self._project_root) / "production" / "shots" / self.sequence / self.shot / "workfiles" / self.step
            )
        elif entity_type == fxentities.entity.task and self.sequence and self.shot and self.step and self.task:
            path = (
                Path(self._project_root)
                / "production"
                / "shots"
                / self.sequence
                / self.shot
                / "workfiles"
                / self.step
                / self.task
            )
        elif (
            entity_type == fxentities.entity.workfile
            and self.sequence
            and self.shot
            and self.step
            and self.task
            and self.workfile
        ):
            path = (
                Path(self._project_root)
                / "production"
                / "shots"
                / self.sequence
                / self.shot
                / "workfiles"
                / self.step
                / self.task
                / self.workfile
            )
        else:
            return

        if not path.exists():
            return

        # Retrieve the metadata
        path = path.resolve().absolute().as_posix()
        metadata_data = fxfiles.get_all_metadata(path)

        # Prepare the table
        table_widget = QTableWidget()
        table_widget.setColumnCount(3)
        table_widget.setRowCount(len(metadata_data))
        table_widget.setHorizontalHeaderLabels(["Label", "Internal", "Value"])
        horizontal_header = table_widget.horizontalHeader()
        tooltips = [
            "<b>Label</b><hr>The metadata key label.",
            "<b>Internal</b><hr>The metadata key internal name.",
            "<b>Value</b><hr>The metadata value.",
        ]
        for index, tooltip in enumerate(tooltips):
            horizontal_header.model().setHeaderData(index, Qt.Horizontal, tooltip, Qt.ToolTipRole)
        horizontal_header.setStretchLastSection(True)
        # horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        table_widget.verticalHeader().setVisible(False)

        font_bold = QFont()
        font_bold.setBold(True)
        font_code = QFont("Courier New")
        font_code.setStyleHint(QFont.TypeWriter)

        for row, (key, value) in enumerate(metadata_data.items()):
            # Key
            key_item = QTableWidgetItem(key.capitalize().replace("_", " "))
            key_item.setFont(font_bold)

            # Internal
            internal_name_item = QTableWidgetItem(key)
            internal_name_item.setFont(font_code)

            # Value
            type = fxfiles.get_metadata_type(key, value)
            if type == str:
                value_item = QTableWidgetItem(value)
                value_item.setIcon(fxicons.get_icon("font_download", color="#ffffff"))
            elif type == int:
                value_item = QTableWidgetItem(value)
                value_item.setIcon(fxicons.get_icon("looks_one", color="#ffc107"))
            elif type == float:
                value_item = QTableWidgetItem(value)
                value_item.setIcon(fxicons.get_icon("looks_two", color="#03a9f4"))
            elif type == dict:
                value_item = QTableWidgetItem(str(value))
                value_item.setIcon(fxicons.get_icon("book", color="#8bc34a"))
            elif type == list:
                value_item = QTableWidgetItem(str(value))
                value_item.setIcon(fxicons.get_icon("view_list", color="#3f51b5"))
            else:
                value_item = QTableWidgetItem(value)
                value_item.setIcon(fxicons.get_icon("font_download", color="#ffffff"))

            # Set flags to make the item non-editable but selectable
            non_editable_flag = Qt.ItemIsEnabled
            key_item.setFlags(non_editable_flag)
            value_item.setFlags(non_editable_flag)
            internal_name_item.setFlags(non_editable_flag)

            # Add the items to the table
            table_widget.setItem(row, 0, key_item)
            table_widget.setItem(row, 1, internal_name_item)
            table_widget.setItem(row, 2, value_item)

        # Sort the table widget
        table_widget.setSortingEnabled(True)

        # Clear the layout and add the table widget
        layout = self.group_box_info.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        layout.addWidget(table_widget)

    # ' Contextual menus
    # Shots
    def _on_shots_context_menu(self, point: QPoint):
        # Create the context menu
        context_menu = QMenu(self)

        # Define actions
        action_create_shot = fxguiutils.create_action(
            context_menu,
            "Create Shot",
            fxicons.get_icon("add_photo_alternate"),
            self.create_shot,
        )
        action_edit_shot = fxguiutils.create_action(
            context_menu,
            "Edit Shot",
            fxicons.get_icon("edit"),
            self.edit_shot,
        )
        action_delete_shot = fxguiutils.create_action(
            context_menu,
            "Delete Shot",
            fxicons.get_icon("delete"),
            self.delete_shot,
        )
        action_expand_all = fxguiutils.create_action(
            context_menu,
            "Expand All",
            fxicons.get_icon("unfold_more"),
            lambda: self.expand_all(self.tree_widget_shots),
        )
        action_collapse_all = fxguiutils.create_action(
            context_menu,
            "Collapse All",
            fxicons.get_icon("unfold_less"),
            lambda: self.collapse_all(self.tree_widget_shots),
        )
        action_show_in_file_browser = fxguiutils.create_action(
            context_menu,
            "Show in File Browser",
            fxicons.get_icon("open_in_new"),
            lambda: self.open_file_or_folder(
                Path(self.tree_widget_shots.currentItem().data(1, Qt.UserRole)).parent.resolve().as_posix()
                if self.tree_widget_shots.currentItem()
                else fxcore.get_project().get("FXQUINOX_PROJECT_SHOTS", None)
            ),
        )

        # Add actions to the context menu
        context_menu.addAction(action_create_shot)
        context_menu.addSeparator()
        context_menu.addAction(action_edit_shot)
        context_menu.addAction(action_delete_shot)
        context_menu.addSeparator()
        context_menu.addAction(action_expand_all)
        context_menu.addAction(action_collapse_all)
        context_menu.addAction(action_show_in_file_browser)

        # Show the context menu
        context_menu.exec_(self.tree_widget_shots.mapToGlobal(point))

    # Assets
    def _on_assets_context_menu(self, point: QPoint):
        # Similar to on_shots_context_menu, but for assets
        context_menu = QMenu(self)

        # Define actions
        action_create_asset = fxguiutils.create_action(
            context_menu,
            "Create Asset",
            fxicons.get_icon("view_in_ar"),
            None,
        )
        action_edit_asset = fxguiutils.create_action(
            context_menu,
            "Edit Asset",
            fxicons.get_icon("edit"),
            None,
        )
        action_delete_asset = fxguiutils.create_action(
            context_menu,
            "Delete Asset",
            fxicons.get_icon("delete"),
            None,
        )
        action_expand_all = fxguiutils.create_action(
            context_menu,
            "Expand All",
            fxicons.get_icon("unfold_more"),
            lambda: self.expand_all(self.tree_widget_shots),
        )
        action_collapse_all = fxguiutils.create_action(
            context_menu,
            "Collapse All",
            fxicons.get_icon("unfold_less"),
            lambda: self.collapse_all(self.tree_widget_shots),
        )
        action_show_in_file_browser = fxguiutils.create_action(
            context_menu,
            "Show in File Browser",
            fxicons.get_icon("open_in_new"),
            lambda: self.open_file_or_folder(
                Path(self.tree_widget_shots.currentItem().data(1, Qt.UserRole)).parent.resolve().as_posix()
                if self.tree_widget_shots.currentItem()
                else fxcore.get_project().get("FXQUINOX_PROJECT_ASSETS", None)
            ),
        )

        # Add actions to the context menu
        context_menu.addAction(action_create_asset)
        context_menu.addSeparator()
        context_menu.addAction(action_edit_asset)
        context_menu.addAction(action_delete_asset)
        context_menu.addSeparator()
        context_menu.addAction(action_expand_all)
        context_menu.addAction(action_collapse_all)
        context_menu.addAction(action_show_in_file_browser)

        # Show the context menu
        context_menu.exec_(self.tree_widget_assets.mapToGlobal(point))

    # Steps
    def _on_steps_context_menu(self, point: QPoint):
        # Similar to on_shots_context_menu, but for steps
        context_menu = QMenu(self)

        # Define actions
        action_create_step = fxguiutils.create_action(
            context_menu,
            "Create Step",
            fxicons.get_icon("dashboard"),
            self.create_step,
        )
        action_show_in_file_browser = fxguiutils.create_action(
            context_menu,
            "Show in File Browser",
            fxicons.get_icon("open_in_new"),
            lambda: self.open_file_or_folder(
                Path(self.list_steps.currentItem().data(Qt.UserRole + 1)).parent.resolve().as_posix()
                if self.list_steps.currentItem()
                else None
            ),
        )

        # Add actions to the context menu
        context_menu.addAction(action_create_step)
        context_menu.addSeparator()
        context_menu.addAction(action_show_in_file_browser)

        # Show the context menu
        context_menu.exec_(self.list_steps.mapToGlobal(point))

    # Tasks
    def _on_tasks_context_menu(self, point: QPoint):
        context_menu = QMenu(self)

        # Define actions
        action_create_task = fxguiutils.create_action(
            context_menu,
            "Create Task",
            fxicons.get_icon("task_alt"),
            self.create_task,
        )
        action_show_in_file_browser = fxguiutils.create_action(
            context_menu,
            "Show in File Browser",
            fxicons.get_icon("open_in_new"),
            lambda: self.open_file_or_folder(
                Path(self.list_tasks.currentItem().data(Qt.UserRole + 1)).parent.resolve().as_posix()
                if self.list_tasks.currentItem()
                else None
            ),
        )

        # Add actions to the context menu
        context_menu.addAction(action_create_task)
        context_menu.addSeparator()
        context_menu.addAction(action_show_in_file_browser)

        # Show the context menu
        context_menu.exec_(self.list_tasks.mapToGlobal(point))

    # Workfiles
    def _on_workfiles_context_menu(self, point: QPoint):
        context_menu = QMenu(self)

        current_menu = context_menu.addMenu("New Version From Current")
        current_menu.setIcon(fxicons.get_icon("note_add"))

        preset_menu = context_menu.addMenu("New Version From Preset")
        preset_menu.setIcon(fxicons.get_icon("note_add"))

        # Define actions
        action_show_in_file_browser = fxguiutils.create_action(
            context_menu,
            "Show in File Browser",
            fxicons.get_icon("open_in_new"),
            lambda: self.open_file_or_folder(
                Path(self.tree_widget_workfiles.currentItem().data(1, Qt.UserRole)).parent.resolve().as_posix()
                if self.tree_widget_workfiles.currentItem()
                else None
            ),
        )

        workfile_presets = Path(self._project_root) / ".pipeline" / "workfile_presets"
        for workfile_preset in workfile_presets.iterdir():
            if not workfile_preset.is_file():
                continue

            # Get the file extension to determine the type
            file_extension = workfile_preset.suffix.lstrip(".")

            # Skip files without or uncompatible extensions
            if file_extension in ["", "md"]:
                continue

            preset_name = workfile_preset.stem
            workfile_preset_path = workfile_preset.resolve().absolute().as_posix()

            preset_action = fxguiutils.create_action(
                preset_menu,
                preset_name,
                self._get_icon_based_on_type(file_extension),
                partial(self.create_workfile_from_preset, preset_file=workfile_preset_path),
            )
            preset_menu.addAction(preset_action)

        # Add actions to the context menu
        context_menu.addSeparator()
        context_menu.addAction(action_show_in_file_browser)

        # Show the context menu
        context_menu.exec_(self.tree_widget_workfiles.mapToGlobal(point))

    # ' Slot for actions
    # Assets
    def create_asset(self):
        # TODO: Implement asset creation logic here
        pass

    def edit_asset(self):
        # TODO: Implement asset editing logic here
        pass

    def delete_asset(self):
        # TODO: Implement asset deletion logic here

        pass

    # Shots
    def create_shot(self):
        widget = FXCreateShotDialog(
            parent=self,
            project_name=self._project_name,
            project_root=self._project_root,
            project_assets=self._project_assets,
            project_shots=self._project_shots,
            sequence=self.sequence,
        )
        widget.setWindowFlags(widget.windowFlags() | Qt.Window)
        widget.resize(400, 200)
        widget.show()

    def edit_shot(self):
        # Implement shot editing logic here
        pass

    def delete_shot(self):
        # Implement shot deletion logic here
        pass

    # Steps
    def create_step(self):
        if not self.sequence or not self.shot:
            warning = QMessageBox(self)
            warning.setWindowTitle("Create Step")
            warning.setText(
                f"You haven't selected a valid environment:<ul><li>Sequence: <b>{self.sequence}</b></li><li>Shot: <b>{self.shot}</b></li></ul>"
            )
            warning.setIcon(QMessageBox.Warning)
            warning.setStandardButtons(QMessageBox.Ok)
            warning.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Make the text selectable
            warning.exec_()
            return

        widget = FXCreateStepDialog(
            parent=self,
            project_name=self._project_name,
            project_root=self._project_root,
            project_assets=self._project_assets,
            project_shots=self._project_shots,
            asset=self.asset,
            sequence=self.sequence,
            shot=self.shot,
        )
        widget.setWindowFlags(widget.windowFlags() | Qt.Window)
        widget.resize(400, 500)
        widget.show()

    # Tasks
    def create_task(self):
        if not self.sequence or not self.shot or not self.step:
            warning = QMessageBox(self)
            warning.setWindowTitle("Create Task")
            warning.setText(
                f"You haven't selected a valid environment:<ul><li>Sequence: <b>{self.sequence}</b></li><li>Shot: <b>{self.shot}</b></li><li>Step: <b>{self.step}</b></ul>"
            )
            warning.setIcon(QMessageBox.Warning)
            warning.setStandardButtons(QMessageBox.Ok)
            warning.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Make the text selectable
            warning.exec_()
            return

        widget = FXCreateTaskDialog(
            parent=self,
            project_name=self._project_name,
            project_root=self._project_root,
            project_assets=self._project_assets,
            project_shots=self._project_shots,
            asset=self.asset,
            sequence=self.sequence,
            shot=self.shot,
            step=self.step,
        )
        widget.setWindowFlags(widget.windowFlags() | Qt.Window)
        widget.resize(400, 500)
        widget.show()

    # Workfiles
    def create_workfile_from_preset(self, preset_file: str = None):
        """Creates a workfile from the selected file in the tree widget.

        Args:
            file (str, optional): The file to create the workfile from.
                Defaults to `None`.
        """

        if not self.sequence or not self.shot or not self.step or not self.task:
            warning = QMessageBox(self)
            warning.setWindowTitle("Create Workfile")
            warning.setText(
                f"You haven't selected a valid environment:<ul>"
                f"<li>Sequence: <b>{self.sequence}</b></li>"
                f"<li>Shot: <b>{self.shot}</b></li>"
                f"<li>Step: <b>{self.step}</b></li>"
                f"<li>Task: <b>{self.task}</b></li></ul>"
            )
            warning.setIcon(QMessageBox.Warning)
            warning.setStandardButtons(QMessageBox.Ok)
            warning.setTextInteractionFlags(Qt.TextSelectableByMouse)
            warning.exec_()
            return

        # Check if the preset file exists
        preset_file_path = Path(preset_file)
        if not preset_file_path.exists():
            return

        # Iterate through the existing files to get the next version
        worfiles_dir = (
            Path(self._project_root)
            / "production"
            / "shots"
            / self.sequence
            / self.shot
            / "workfiles"
            / self.step
            / self.task
        )
        next_version = fxfiles.get_next_version(worfiles_dir, as_string=True)

        # Build the new file name
        new_file_name = f"{self.sequence}_{self.shot}_{self.step}_{self.task}_{next_version}{preset_file_path.suffix}"
        new_file_path = worfiles_dir / new_file_name

        _logger.debug(f"Old file path: '{preset_file_path.resolve().as_posix()}'")
        _logger.debug(f"New file path: '{new_file_path.resolve().as_posix()}'")

        # Copy the preset file to the new file path
        shutil.copy(preset_file_path, new_file_path)

        # Set metadata
        metadata = {
            "creator": "fxquinox",
            "entity": "worfile",
            "name": new_file_name,
            "path": new_file_path.resolve().as_posix(),
            "parent": worfiles_dir.resolve().as_posix(),
            "description": "Workfile",
            "version": next_version,
            "comment": "Created from preset file",
            "user": getpass.getuser(),
        }
        fxfiles.set_multiple_metadata(new_file_path.resolve().as_posix(), metadata)

        self.refresh()

    # Common
    def open_file_or_folder(self, path: str):
        url = QUrl.fromLocalFile(path)
        QDesktopServices.openUrl(url)

    def expand_all(self, tree_widget: QTreeWidget):
        tree_widget.expandAll()

    def collapse_all(self, tree_widget: QTreeWidget):
        tree_widget.collapseAll()


class FXCreateProjectWindow(fxwidgets.FXMainWindow):
    # TODO: Implement the create project window
    pass


class FXCreateShotDialog(QDialog):
    def __init__(
        self, parent=None, project_name=None, project_root=None, project_assets=None, project_shots=None, sequence=None
    ):
        super().__init__(parent)

        # Attributes
        self.project_name = project_name
        self._project_root = project_root
        self._project_assets = project_assets
        self._project_shots = project_shots
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

        ui_file = Path(__file__).parent / "ui" / "create_shot.ui"
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
            fxcore.create_sequence(sequence, self._project_shots)

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


class FXCreateAssetDialog(QDialog):
    # TODO: Implement the create asset window
    pass


class FXCreateStepDialog(QDialog):
    def __init__(
        self,
        parent=None,
        project_name=None,
        project_root=None,
        project_assets=None,
        project_shots=None,
        asset=None,
        sequence=None,
        shot=None,
    ):
        super().__init__(parent)

        # Attributes
        self.project_name = project_name
        self._project_root = project_root
        self._project_assets = project_assets
        self._project_shots = project_shots

        self.asset = asset
        self.sequence = sequence
        self.shot = shot

        # Methods
        self.setModal(True)

        self._create_ui()
        self._rename_ui()
        self._modify_ui()
        self._handle_connections()
        self._populate_steps()

        _logger.info("Initialized create step")

    def _create_ui(self):
        """_summary_"""

        ui_file = Path(__file__).parent / "ui" / "create_step.ui"
        self.ui = fxguiutils.load_ui(self, str(ui_file))
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)
        self.setWindowTitle(f"Create Step | {self.sequence} - {self.shot}")

    def _rename_ui(self):
        """_summary_"""

        self.list_steps: QListWidget = self.ui.list_steps
        self.checkbox_add_tasks: QCheckBox = self.ui.checkbox_add_tasks
        self.list_tasks: QListWidget = self.ui.list_tasks
        self.button_box: QButtonGroup = self.ui.button_box

    def _modify_ui(self):
        # Contains some slots connections, to avoid iterating multiple times
        # over the buttons
        for button in self.button_box.buttons():
            role = self.button_box.buttonRole(button)
            if role == QDialogButtonBox.AcceptRole:
                button.setIcon(fxicons.get_icon("check", color="#8fc550"))
                button.setText("Create")
                # Create step
                button.clicked.connect(self._create_step)
            elif role == QDialogButtonBox.RejectRole:
                button.setIcon(fxicons.get_icon("close", color="#ec0811"))
                # Close
                button.clicked.connect(self.close)

    def _handle_connections(self):
        """_summary_"""

        self.list_steps.currentItemChanged.connect(self._populate_tasks)
        self.checkbox_add_tasks.stateChanged.connect(
            lambda: self.list_tasks.setEnabled(self.checkbox_add_tasks.isChecked())
        )

    def _populate_steps(self):
        # Parse the `steps.yaml` file
        steps_file = Path(self._project_root) / ".pipeline" / "project_config" / "steps.yaml"
        if not steps_file.exists():
            return
        steps_data = yaml.safe_load(steps_file.read_text())

        # Gather existing step names
        parent = self.parent()
        if parent:
            existing_steps = {parent.list_steps.item(i).text() for i in range(parent.list_steps.count())}
        else:
            existing_steps = []

        for step in steps_data["steps"]:
            step_name = step.get("name_long", "Unknown Step")
            if step_name not in existing_steps:
                step_item = QListWidgetItem(step_name)
                step_item.setIcon(
                    fxicons.get_icon(step.get("icon", "check_box_outline_blank"), color=step.get("color", "#ffffff"))
                )
                step_item.setData(Qt.UserRole, step)
                self.list_steps.addItem(step_item)

    def _populate_tasks(self, current, previous):
        self.list_tasks.clear()  # Clear existing tasks
        if current is not None:
            step = current.data(Qt.UserRole)
            for task in step["tasks"]:
                task_item = QListWidgetItem(task.get("name", "Unknown Task"))
                task_item.setIcon(fxicons.get_icon("task_alt"))
                task_item.setData(Qt.UserRole, task)
                self.list_tasks.addItem(task_item)

    def _create_step(self):
        # Get the selected step
        _logger.debug(f"Asset: '{self.asset}', sequence: '{self.sequence}', shot: '{self.shot}'")
        step = self.list_steps.currentItem().text()

        # Create the step
        workfiles_dir = Path(self._project_root) / "production" / "shots" / self.sequence / self.shot / "workfiles"
        step = fxcore.create_step(step, workfiles_dir, self)
        if not step:
            return

        step_dir = workfiles_dir / step
        if self.checkbox_add_tasks.isChecked():
            for i in range(self.list_tasks.count()):
                task = self.list_tasks.item(i).text()
                fxcore.create_task(task, step_dir, self)

        # Refresh parent and close QDialog on completion
        parent = self.parent()
        if parent:
            parent.refresh()

        self.close()


class FXCreateTaskDialog(QDialog):
    def __init__(
        self,
        parent=None,
        project_name=None,
        project_root=None,
        project_assets=None,
        project_shots=None,
        asset=None,
        sequence=None,
        shot=None,
        step=None,
    ):
        super().__init__(parent)

        # Attributes
        self.project_name = project_name
        self._project_root = project_root
        self._project_assets = project_assets
        self._project_shots = project_shots

        self.asset = asset
        self.sequence = sequence
        self.shot = shot
        self.step = step

        # Methods
        self.setModal(True)

        self._create_ui()
        self._rename_ui()
        self._modify_ui()
        self._populate_tasks()

        _logger.info("Initialized create task")

    def _create_ui(self):
        """_summary_"""

        ui_file = Path(__file__).parent / "ui" / "create_task.ui"
        self.ui = fxguiutils.load_ui(self, str(ui_file))
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)
        self.setWindowTitle(f"Create Task | {self.sequence} - {self.shot} - {self.step}")

    def _rename_ui(self):
        """_summary_"""

        self.list_tasks: QListWidget = self.ui.list_tasks
        self.button_box: QButtonGroup = self.ui.button_box

    def _modify_ui(self):
        # Contains some slots connections, to avoid iterating multiple times
        # over the buttons
        for button in self.button_box.buttons():
            role = self.button_box.buttonRole(button)
            if role == QDialogButtonBox.AcceptRole:
                button.setIcon(fxicons.get_icon("check", color="#8fc550"))
                button.setText("Create")
                # Create task
                button.clicked.connect(self._create_task)
            elif role == QDialogButtonBox.RejectRole:
                button.setIcon(fxicons.get_icon("close", color="#ec0811"))
                # Close
                button.clicked.connect(self.close)

    def _populate_tasks(self):
        self.list_tasks.clear()  # Clear existing tasks

        steps_file = Path(self._project_root) / ".pipeline" / "project_config" / "steps.yaml"
        if not steps_file.exists():
            return

        steps_data = yaml.safe_load(steps_file.read_text())

        # Find the step that matches self.step
        current_step = next((step for step in steps_data["steps"] if step["name_long"] == self.step), None)
        if not current_step:
            return  # If the step is not found, exit the function

        # Gather existing task names
        parent = self.parent()
        if parent:
            existing_tasks = {parent.list_tasks.item(i).text() for i in range(parent.list_tasks.count())}
        else:
            existing_tasks = []

        # Iterate over the tasks of the found step
        for task in current_step.get("tasks", []):
            task_name = task.get("name", "Unknown Task")
            if task_name not in existing_tasks:  # Check if the task is not already in the list
                task_item = QListWidgetItem(task_name)
                task_item.setIcon(fxicons.get_icon("task_alt"))
                task_item.setData(Qt.UserRole, task)
                self.list_tasks.addItem(task_item)
                # existing_tasks.add(task_name)  # Add the new task name to the set of existing tasks

    def _create_task(self):
        # Get the selected task
        _logger.debug(f"Asset: '{self.asset}', sequence: '{self.sequence}', shot: '{self.shot}', step: '{self.step}'")
        task = self.list_tasks.currentItem().text()

        # Create the task
        step_dir = (
            Path(self._project_root) / "production" / "shots" / self.sequence / self.shot / "workfiles" / self.step
        )
        task = fxcore.create_task(task, step_dir, self)
        if not task:
            return

        # Refresh parent and close QDialog on completion
        parent = self.parent()
        if parent:
            parent.refresh()

        self.close()


class FXCreateWorkfileDialog(QDialog):
    # TODO: Implement the create workfile window
    pass
