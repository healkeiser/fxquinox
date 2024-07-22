# Built-in
from datetime import datetime
from functools import partial
import getpass
from logging import warn
import os
from pathlib import Path
import shutil
import sys
from typing import Optional, Tuple, Dict

from fxquinox.ui.fxwidgets.fxdialog import FXDialog

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
from fxquinox import fxcore, fxentities, fxenvironment, fxfiles, fxlog, fxutils
from fxquinox.ui.fxwidgets.fxcreateshotdialog import FXCreateShotDialog

# from fxquinox.ui.fxwidgets.fxcreateassetdialog import FXCreateAssetDialog
from fxquinox.ui.fxwidgets.fxcreatestepdialog import FXCreateStepDialog
from fxquinox.ui.fxwidgets.fxcreatetaskdialog import FXCreateTaskDialog
from fxquinox.ui.fxwidgets.fxmetadatatablewidget import FXMetadataTableWidget
from fxquinox.ui.fxwidgets.fxthumbnaildelegate import FXThumbnailItemDelegate


# Log
_logger = fxlog.get_logger("fxprojectbrowser")
_logger.setLevel(fxlog.DEBUG)


class FXProjectBrowserWindow(fxwidgets.FXMainWindow):
    """The The Fxquinox project browser class. Provides a window for browsing
    the project assets, shots, steps, tasks, and workfiles.

    Args:
        parent (Optional[QWidget], optional): The parent widget.
            Defaults to `None`.
        icon (Optional[str], optional): The icon name. Defaults to `None`.
        title (Optional[str], optional): The window title. Defaults to `None`.
        size (Optional[int], optional): The window size. Defaults to `None`.
        documentation (Optional[str], optional): The documentation URL.
            Defaults to `None`.
        project (Optional[str], optional): The project name. Defaults to `None`.
        version (Optional[str], optional): The version number.
            Defaults to `None`.
        company (Optional[str], optional): The company name. Defaults to `None`.
        color_a (Optional[str], optional): The color A for the window.
            Defaults to `None`.
        color_b (Optional[str], optional): The color B for the window.
            Defaults to `None`.
        ui_file (Optional[str], optional): The UI file to load.
            Defaults to `None`.
        dcc (fxentities.DCC, optional): The DCC to use.
            Defaults to `fxentities.DCC.standalone`.

    Attributes:
        project_info (dict): The project information.
        dcc (fxentities.DCC): The DCC to use.
        asset (Optional[str]): The current asset.
        sequence (str): The current sequence.
        shot (str): The current shot.
        step (str): The current step.
        task (str): The current task.
        workfile (str): The current workfile.
    """

    _instance = None

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
        #
        project_info: Optional[Dict] = None,
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

        # Singleton
        FXProjectBrowserWindow._instance = self

        # Attributes
        self.project_info = project_info
        self.dcc = dcc

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
        self.workfile: str = None
        self.workfile_path: str = None

        # Methods
        self._get_project()
        self._rename_ui()
        self._handle_connections()
        self._create_icons()
        self._modify_ui()
        self._filter_workfiles_by_type()
        self._populate_assets()
        self._populate_shots()

        self.status_line.hide()
        self.statusBar().showMessage(
            "Initialized project browser", self.INFO, logger=_logger
        )

    def _get_project(self) -> None:
        """Gets the project information from the environment variables or the
        configuration file.
        """

        if all(not value for value in self.project_info.values()):
            self.project_info = fxcore.get_project()
        self._project_root = self.project_info.get(
            "FXQUINOX_PROJECT_ROOT", None
        )
        self._project_name = self.project_info.get(
            "FXQUINOX_PROJECT_NAME", None
        )
        self._project_assets_path = self.project_info.get(
            "FXQUINOX_PROJECT_ASSETS_PATH", None
        )
        self._project_shots_path = self.project_info.get(
            "FXQUINOX_PROJECT_SHOTS_PATH", None
        )

        _logger.debug("Get project")
        _logger.debug(
            f"$FXQUINOX_PROJECT_ROOT: '{os.environ.get('FXQUINOX_PROJECT_ROOT', None)}'"
        )
        _logger.debug(
            f"$FXQUINOX_PROJECT_NAME: '{os.environ.get('FXQUINOX_PROJECT_NAME', None)}'"
        )
        _logger.debug(
            f"$FXQUINOX_PROJECT_ASSETS_PATH: '{os.environ.get('FXQUINOX_PROJECT_ASSETS_PATH', None)}'"
        )
        _logger.debug(
            f"$FXQUINOX_PROJECT_SHOTS_PATH: '{os.environ.get('FXQUINOX_PROJECT_SHOTS_PATH', None)}'"
        )

    def _rename_ui(self):
        """_summary_"""

        self.label_project: QLabel = self.ui.label_project
        self.line_project: QFrame = self.ui.line_project
        #
        self.tab_assets_shots: QTabWidget = self.ui.tab_assets_shots
        #
        self.tab_assets: QWidget = self.ui.tab_assets
        self.label_icon_filter_assets: QLabel = (
            self.ui.label_icon_filter_assets
        )
        self.line_edit_filter_assets: QLineEdit = (
            self.ui.line_edit_filter_assets
        )
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
        self.checkbox_display_latest_worfiles: QCheckBox = (
            self.ui.checkbox_display_latest_worfiles
        )
        self.label_icon_filter_workfiles: QLabel = (
            self.ui.label_icon_filter_workfiles
        )
        self.combobox_filter_workfiles: QComboBox = (
            self.ui.combobox_filter_workfiles
        )
        self.tree_widget_workfiles: QTreeWidget = self.ui.tree_widget_workfiles
        #
        self.group_box_info: QGroupBox = self.ui.group_box_info

    def _handle_connections(self):
        # Filter assets
        self.line_edit_filter_assets.textChanged.connect(
            lambda: fxguiutils.filter_tree(
                self.line_edit_filter_assets, self.tree_widget_assets, 0
            )
        )

        # Filter shots
        self.line_edit_filter_shots.textChanged.connect(
            lambda: fxguiutils.filter_tree(
                self.line_edit_filter_shots, self.tree_widget_shots, 0
            )
        )

        # Assets
        self.tree_widget_assets.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget_assets.customContextMenuRequested.connect(
            self._on_assets_context_menu
        )
        self.tree_widget_assets.itemSelectionChanged.connect(
            self._get_current_asset
        )
        self.tree_widget_assets.itemSelectionChanged.connect(
            lambda: self._display_metadata(fxentities.entity.asset)
        )

        # Shots
        self.tree_widget_shots.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget_shots.customContextMenuRequested.connect(
            self._on_shots_context_menu
        )
        self.tree_widget_shots.itemSelectionChanged.connect(
            self._get_current_sequence_and_shot
        )
        self.tree_widget_shots.itemSelectionChanged.connect(
            self._populate_steps
        )
        # Handle metadata for both sequence and shot
        self.tree_widget_shots.itemSelectionChanged.connect(
            self._handle_sequence_shot_selection
        )

        # Steps
        self.list_steps.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_steps.customContextMenuRequested.connect(
            self._on_steps_context_menu
        )
        self.list_steps.itemSelectionChanged.connect(self._get_current_step)
        self.list_steps.itemSelectionChanged.connect(self._populate_tasks)
        self.list_steps.itemSelectionChanged.connect(
            lambda: self._display_metadata(fxentities.entity.step)
        )

        # Tasks
        self.list_tasks.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_tasks.customContextMenuRequested.connect(
            self._on_tasks_context_menu
        )
        self.list_tasks.itemSelectionChanged.connect(self._get_current_task)
        self.list_tasks.itemSelectionChanged.connect(self._populate_workfiles)
        self.list_tasks.itemSelectionChanged.connect(
            lambda: self._display_metadata(fxentities.entity.task)
        )

        # Workfiles
        self.checkbox_display_latest_worfiles.stateChanged.connect(
            self._on_show_latest_workfile_changed
        )
        self.combobox_filter_workfiles.currentIndexChanged.connect(
            self._on_filter_workfiles_by_type_changed
        )
        self.combobox_filter_workfiles.currentIndexChanged.connect(
            self._populate_workfiles
        )
        self.tree_widget_workfiles.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget_workfiles.customContextMenuRequested.connect(
            self._on_workfiles_context_menu
        )
        self.tree_widget_workfiles.itemSelectionChanged.connect(
            self._get_current_workfile
        )
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
            [
                "Workfiles",
                "Version",
                "Comment",
                "Date Created",
                "Date Modified",
                "User",
                "Size",
            ]
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

    def _modify_toolbar(self):
        """Modifies the toolbar."""

        self.toolbar.addAction()

    #
    def refresh(self):
        # Display statusbar message and change icon
        # self.statusBar().showMessage("Refreshing...", fxwidgets.INFO, logger=_logger)

        # Methods to run
        self._populate_assets()
        self._populate_shots()
        # self._populate_steps()
        # self._populate_tasks()
        # self._populate_workfiles()

    # ' Populating methods
    # Shots
    def _populate_shots(self) -> None:
        """Populates the shots tree widget with the shots in the project."""

        # Delegate
        self.tree_widget_shots.setItemDelegate(FXThumbnailItemDelegate())
        # ! Set thumbnail by using the `Qt.UserRole + 2` role

        # Store the states (expanded and selected items)
        expanded_states = self._store_expanded_states(self.tree_widget_shots)
        selected_states = self._store_selection_state_tree(
            self.tree_widget_shots
        )

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
            sequence_item.setData(
                0, Qt.UserRole + 1, False
            )  # Disable thumbnail for sequence

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
                shot_item.setData(
                    0, Qt.UserRole + 1, True
                )  # Enable thumbnail for shot
                # Set thumbnail
                thumbnail_path = fxfiles.get_metadata(shot_path, "thumbnail")
                if thumbnail_path:
                    shot_item.setData(0, Qt.UserRole + 2, thumbnail_path)

                # Set tooltip
                shot_item.setToolTip(
                    0,
                    f"<b>{shot.name}</b><hr><b>Entity</b>: Shot<br><br><b>Path</b>: {shot_path}",
                )

        # Expand all items by default
        self._expand_all_items(self.tree_widget_shots)

        # Restore states
        self._restore_expanded_states(self.tree_widget_shots, expanded_states)
        self._restore_selection_state_tree(
            self.tree_widget_shots, selected_states
        )

        # After populating the tree, select the first item if it exists
        # self._select_first_child_item_in_tree(self.tree_widget_shots)
        # self._get_current_sequence_and_shot()
        # self._populate_steps()

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

        self.entity = "shot"
        self.asset = None
        self.asset_path = None
        self.sequence = sequence.text(0) if sequence else None
        self.sequence_path = (
            sequence.data(1, Qt.UserRole) if sequence else None
        )
        self.shot = shot.text(0) if shot else None
        self.shot_path = shot.data(1, Qt.UserRole) if shot else None

        _logger.debug(f"Get current sequence and shot")
        _logger.debug(f"Entity: '{self.entity}'")
        _logger.debug(f"Asset: '{self.asset}'")
        _logger.debug(f"Asset path: '{self.asset_path}'")
        _logger.debug(f"Sequence: '{self.sequence}'")
        _logger.debug(f"Sequence path: '{self.sequence_path}'")
        _logger.debug(f"Shot: '{self.shot}'")
        _logger.debug(f"Shot path: '{self.shot_path}'")

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

        self.entity = "asset"
        self.asset = current_item.text(0)
        self.asset_path = current_item.data(1, Qt.UserRole)
        self.sequence = None
        self.sequence_path = None
        self.shot = None
        self.shot_path = None

        _logger.debug(f"Get current asset")
        _logger.debug(f"Entity: '{self.entity}'")
        _logger.debug(f"Asset: '{self.asset}'")
        _logger.debug(f"Asset path: '{self.asset_path}'")
        _logger.debug(f"Sequence: '{self.sequence}'")
        _logger.debug(f"Sequence path: '{self.sequence_path}'")
        _logger.debug(f"Shot: '{self.shot}'")
        _logger.debug(f"Shot path: '{self.shot_path}'")

        return self.asset

    # Steps
    def _populate_steps(self):
        # Clear
        self.list_steps.clear()

        # Check if the sequence and shot are set
        if self.sequence is None or self.shot is None:
            return

        # Check if the steps directory exists
        workfiles_dir = (
            Path(self._project_root)
            / "production"
            / "shots"
            / self.sequence
            / self.shot
            / "workfiles"
        )
        if not workfiles_dir.exists():
            return

        # Get the steps data for color and icon
        steps_file = (
            Path(self._project_root)
            / ".pipeline"
            / "project_config"
            / "steps.yaml"
        )
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
                (
                    _step
                    for _step in steps_data["steps"]
                    if _step.get("name_long", None) == step_name
                ),
                None,
            )

            if matching_step:
                # Set the icon for the matching step
                step_item.setIcon(
                    fxicons.get_icon(
                        matching_step.get("icon", "check_box_outline_blank"),
                        # color=matching_step.get("color", "#ffffff"),
                    )
                )
            else:
                # Set a default icon if no matching step is found
                step_item.setIcon(fxicons.get_icon("check_box_outline_blank"))

            step_path = step.resolve().absolute().as_posix()
            # Set data
            step_item.setData(Qt.UserRole, fxentities.entity.step)
            step_item.setData(Qt.UserRole + 1, step_path)
            step_item.setToolTip(
                f"<b>{step.name}</b><hr><b>Entity</b>: Step<br><br><b>Path</b>: {step_path}"
            )
            self.list_steps.addItem(step_item)

        # After populating the list, select the first item if it exists
        # self._select_first_item_in_list(self.list_steps)
        # self._get_current_step()
        # self._populate_tasks()

    def _get_current_step(self) -> str:
        """Returns the current step selected in the list widget.

        Returns:
            str: The name of the step.
        """

        current_item = self.list_steps.currentItem()
        if current_item is None:
            return None

        self.step = current_item.text()
        self.step_path = current_item.data(Qt.UserRole + 1)

        _logger.debug(f"Get current step")
        _logger.debug(f"Step: '{self.step}'")
        _logger.debug(f"Step path: '{self.step_path}'")

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
            Path(self._project_root)
            / "production"
            / "shots"
            / self.sequence
            / self.shot
            / "workfiles"
            / self.step
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
            task_item.setToolTip(
                f"<b>{task.name}</b><hr><b>Entity</b>: Task<br><br><b>Path</b>: {task_path}"
            )
            self.list_tasks.addItem(task_item)

        # After populating the list, select the first item if it exists
        # self._select_first_item_in_list(self.list_tasks)
        # self._get_current_task()
        # self._populate_workfiles()

    def _get_current_task(self) -> str:
        """Returns the current task selected in the list widget.

        Returns:
            str: The name of the task.
        """

        current_item = self.list_tasks.currentItem()
        if current_item is None:
            return None

        self.task = current_item.text()
        self.task_path = current_item.data(Qt.UserRole + 1)

        _logger.debug(f"Get current task")
        _logger.debug(f"Task: '{self.task}'")
        _logger.debug(f"Task path: '{self.task_path}'")

        return self.task

    # Workfiles
    def _populate_workfiles(self):
        # Clear
        self.tree_widget_workfiles.clear()

        # Check if the sequence, shot, step, and task are set
        if (
            self.sequence is None
            or self.shot is None
            or self.step is None
            or self.task is None
        ):
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

        def format_size(
            bytes, units=["bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
        ) -> str:
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
                if workfile_type == "Blender" and not workfile.suffix.lstrip(
                    "."
                ) in ["blend"]:
                    continue
                elif workfile_type == "Houdini" and not workfile.suffix.lstrip(
                    "."
                ) in ["hip", "hipnc", "hiplc"]:
                    continue
                elif workfile_type == "Maya" and not workfile.suffix.lstrip(
                    "."
                ) in ["ma", "mb"]:
                    continue
                elif workfile_type == "Nuke" and not workfile.suffix.lstrip(
                    "."
                ) in ["nk"]:
                    continue
                elif (
                    workfile_type == "Photoshop"
                    and not workfile.suffix.lstrip(".") in ["psd"]
                ):
                    continue
                elif (
                    workfile_type == "Substance Painter"
                    and not workfile.suffix.lstrip(".") in ["spp"]
                ):
                    continue

            workfile_name = workfile.name
            workfile_type = workfile.suffix.lstrip(".")
            workfile_item = QTreeWidgetItem(self.tree_widget_workfiles)
            workfile_item.setText(0, workfile_name)
            workfile_path = workfile.resolve().absolute().as_posix()

            # Workfile
            workfile_item.setIcon(
                0, self._get_icon_based_on_type(workfile_type)
            )
            workfile_item.setFont(0, font_bold)

            # Version
            workfile_item.setText(
                1, fxfiles.get_metadata(workfile_path, "version")
            )

            # Comment
            workfile_item.setText(
                2, fxfiles.get_metadata(workfile_path, "comment")
            )
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
            workfile_item.setText(
                5, fxfiles.get_metadata(workfile_path, "user")
            )

            # File size
            workfile_item.setText(6, format_size(workfile.stat().st_size))

            # Set data
            workfile_item.setData(0, Qt.UserRole, fxentities.entity.workfile)
            workfile_item.setData(1, Qt.UserRole, workfile_path)

            # Change tooltip and color if the file hasn't been created by fxquinox
            tooltip = f"<b>{workfile_name}</b><hr><b>Entity</b>: Workfile<br><br><b>Path</b>: {workfile_path}"

            if fxfiles.get_metadata(workfile_path, "creator") != "fxquinox":
                workfile_item.setForeground(0, QColor("#ffc107"))
                tooltip += "<br><br><b><font color='#ffc107'>Warning</font></b>: This file was not created by fxquinox."

            # Set tooltip
            workfile_item.setToolTip(0, tooltip)

        extra_space = 5
        for column_index in range(7):
            self.tree_widget_workfiles.resizeColumnToContents(column_index)
            current_width = self.tree_widget_workfiles.columnWidth(
                column_index
            )
            self.tree_widget_workfiles.setColumnWidth(
                column_index, current_width + extra_space
            )

        # After populating the tree, select the first item if it exists
        # self._select_first_item_in_tree(self.tree_widget_workfiles)
        # self._get_current_workfile()

    def _get_icon_based_on_type(self, item_type: str) -> QIcon:
        """Returns an icon based on the item type. To be used when populating
        the workfiles tree widget.

        Args:
            item_type (str): The item type.

        Returns:
            QIcon: The icon.
        """

        path_icons_apps = (
            Path(fxenvironment._FQUINOX_IMAGES) / "icons" / "apps"
        )

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

    def _toggle_latest_workfile_visibility(
        self, show_highest_only: bool
    ) -> None:
        """Toggles the visibility of the latest workfile based on the checkbox
        state.

        Args:
            show_highest_only (bool): If True, only the workfile with the
                highest version will be shown.
        """

        if show_highest_only:
            highest_version = -1
            highest_version_item = None

            # Find the item with the highest version
            for i in range(self.tree_widget_workfiles.topLevelItemCount()):
                item = self.tree_widget_workfiles.topLevelItem(i)

                # e.g., "v001"
                version_str = item.text(1)
                if len(version_str) > 1 and version_str[1:].isdigit():

                    # Convert to int
                    version_num = int(version_str[1:])
                else:
                    # Skip items that don't have a valid version format
                    continue

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

    def _on_show_latest_workfile_changed(self, state: int) -> None:
        """Toggles the visibility of the latest workfile based on the checkbox
        state.

        Args:
            state (int): The state of the checkbox.
        """

        show_highest_only = state == Qt.Checked
        self._toggle_latest_workfile_visibility(show_highest_only)

    def __filter_workfiles_by_type(self, workfile_type: str) -> None:
        """Filters the workfiles based on the workfile type.

        Args:
            workfile_type (str): The workfile type.
        """

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
                if item.data(1, Qt.UserRole).endswith(".ma") or item.data(
                    1, Qt.UserRole
                ).endswith(".mb"):
                    item.setHidden(False)
                else:
                    item.setHidden(True)

        elif workfile_type == "Nuke":
            for i in range(self.tree_widget_workfiles.topLevelItemCount()):
                item = self.tree_widget_workfiles.topLevelItem(i)
                if item.data(1, Qt.UserRole).endswith(".nk") or item.data(
                    1, Qt.UserRole
                ).endswith(".nknc"):
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

    def _filter_workfiles_by_type(self) -> None:
        """Filters the workfiles based on the workfile type."""

        if self.dcc == fxentities.DCC.standalone:
            match_string = "All"
            self.combobox_filter_workfiles.setEnabled(True)
        elif self.dcc == fxentities.DCC.blender:
            match_string = "Blender"
            self.combobox_filter_workfiles.setEnabled(False)
        elif self.dcc == fxentities.DCC.houdini:
            match_string = "Houdini"
            self.combobox_filter_workfiles.setEnabled(False)
        elif self.dcc == fxentities.DCC.maya:
            match_string = "Maya"
            self.combobox_filter_workfiles.setEnabled(False)
        elif self.dcc == fxentities.DCC.nuke:
            match_string = "Nuke"
            self.combobox_filter_workfiles.setEnabled(False)

        if match_string:
            for index in range(self.combobox_filter_workfiles.count()):
                # Get the text of the current item
                item_text = self.combobox_filter_workfiles.itemText(index)
                # Check if the item text matches the DCC
                if match_string in item_text:
                    # Step 3: Set the current index to select the item
                    self.combobox_filter_workfiles.setCurrentIndex(index)
                    break

    def _on_filter_workfiles_by_type_changed(self) -> None:
        """Modifies the UI elements based on the workfile type selected."""

        workfile_type = self.combobox_filter_workfiles.currentText()
        if workfile_type != "All":
            self.label_icon_filter_workfiles.setPixmap(
                fxicons.get_pixmap("filter_alt", 18, color="#ffc107")
            )
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
        self.workfile_path = current_item.data(1, Qt.UserRole)

        _logger.debug(f"Get current workfile")
        _logger.debug(f"Workfile: '{self.workfile}'")

        return self.workfile

    def _set_environment_variables(self):
        """Set the environment variables after the workfile is opened."""

        # Environment variables
        env_vars = {
            "FXQUINOX_ENTITY": self.entity,
            "FXQUINOX_ASSET": self.asset,
            "FXQUINOX_ASSET_PATH": self.asset_path,
            "FXQUINOX_SEQUENCE": self.sequence,
            "FXQUINOX_SEQUENCE_PATH": self.sequence_path,
            "FXQUINOX_SHOT": self.shot,
            "FXQUINOX_SHOT_PATH": self.shot_path,
            "FXQUINOX_STEP": self.step,
            "FXQUINOX_STEP_PATH": self.step_path,
            "FXQUINOX_TASK": self.task,
            "FXQUINOX_TASK_PATH": self.task_path,
            "FXQUINOX_WORKFILE": self.workfile,
            "FXQUINOX_WORKFILE_PATH": self.workfile_path,
        }

        # Set environment variables
        for var, value in env_vars.items():
            os.environ[var] = value if value else ""
            _logger.debug(f"Set environment variable: '{var}' = '{value}'")

    # ? Define functions for each DCC opening
    def _open_workfile_standalone(self, file_path: str) -> None:
        """Opens the workfile in the standalone DCC application.

        Args:
            file_path (str): The path to the workfile.
        """

        fxutils.open_directory(path=file_path)

    def _open_workfile_blender(self, file_path: str) -> None:
        """Opens the workfile in Blender.

        Args:
            file_path (str): The path to the workfile.
        """

        try:
            import bpy  # type: ignore

            bpy.ops.wm.open_mainfile(filepath=file_path)
            self.showMinimized()
        except ImportError as exception:
            _logger.error(f"Error: {str(exception)}")

    def _open_workfile_houdini(self, file_path: str) -> None:
        """Opens the workfile in Houdini.

        Args:
            file_path (str): The path to the workfile.
        """

        try:
            import hou  # type: ignore

            hou.hipFile.load(file_path)
            self.showMinimized()
        except ImportError as exception:
            _logger.error(f"Error: {str(exception)}")

    def _open_workfile_maya(self, file_path: str) -> None:
        """Opens the workfile in Maya.

        Args:
            file_path (str): The path to the workfile.
        """

        try:
            import maya.cmds as cmds  # type: ignore

            cmds.file(file_path, open=True, force=True)
            self.showMinimized()
        except ImportError as exception:
            _logger.error(f"Error: {str(exception)}")

    def _open_workfile_nuke(self, file_path: str) -> None:
        """Opens the workfile in Nuke.

        Args:
            file_path (str): The path to the workfile.
        """

        try:
            import nuke  # type: ignore

            nuke.scriptOpen(file_path)
            self.showMinimized()
        except ImportError as exception:
            _logger.error(f"Error: {str(exception)}")

    def _open_workfile(self):
        """Opens the selected workfile based on the DCC."""

        # TODO: Implement open workfile method using the defined
        # TODO: executables in the launcher (inside the project config)
        item = self.tree_widget_workfiles.currentItem()
        if item is None:
            return

        if not Path(self.workfile_path).is_file():
            return

        # Open the workfile based on the DCC
        # Standalone
        if self.dcc == fxentities.DCC.standalone:
            self._open_workfile_standalone(self.workfile_path)
            self._set_environment_variables()

        # Blender
        elif self.dcc == fxentities.DCC.blender:
            self._open_workfile_blender(self.workfile_path)
            self._set_environment_variables()

        # Houdini
        elif self.dcc == fxentities.DCC.houdini:
            self._open_workfile_houdini(self.workfile_path)
            self._set_environment_variables()

        # Maya
        elif self.dcc == fxentities.DCC.maya:
            self._open_workfile_maya(self.workfile_path)
            self._set_environment_variables()

        # Nuke
        elif self.dcc == fxentities.DCC.nuke:
            self._open_workfile_nuke(self.workfile_path)
            self._set_environment_variables()

        else:
            return

    # Common

    def _on_item_clicked(
        self, item: QTreeWidgetItem, tree: QTreeWidget, entity: fxentities.DCC
    ) -> None:
        """Displays the metadata of the selected item in the tree widget.

        Args:
            item (QTreeWidgetItem): The item clicked.
            tree (QTreeWidget): The tree widget.
            entity (fxentities.DCC): The entity.
        """

        selected_items = tree.selectedItems()
        if selected_items and item == selected_items[0]:
            self._display_metadata(entity)

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
            tree_widget.setCurrentItem(first_item)
            tree_widget.scrollToItem(first_item)
            tree_widget.setFocus()

    def _select_first_child_item_in_tree(self, tree_widget: QTreeWidget):
        """Selects the second child item of the first top-level item in the tree widget, if it exists.

        Args:
            tree_widget (QTreeWidget): The tree widget.
        """

        if tree_widget.topLevelItemCount() > 0:
            first_top_level_item = tree_widget.topLevelItem(0)
            if first_top_level_item.childCount() > 0:
                tree_widget.clearSelection()
                first_child_item = first_top_level_item.child(
                    0
                )  # Get the first child
                tree_widget.setSelectionMode(QAbstractItemView.SingleSelection)
                first_child_item.setSelected(True)
                tree_widget.setCurrentItem(first_child_item)
                tree_widget.scrollToItem(first_child_item)
                tree_widget.setFocus()

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
            list_widget.setCurrentItem(first_item)
            list_widget.setFocus()

    # States for QTreeWidget expansion
    def _expand_all_items(self, tree_widget: QTreeWidget) -> None:
        """Expands all items in the given tree widget.

        Args:
            tree_widget (QTreeWidget): The tree widget to expand.
        """

        for i in range(tree_widget.topLevelItemCount()):
            item = tree_widget.topLevelItem(i)
            tree_widget.expandItem(item)

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
            tree_widget (QTreeWidget): The tree widget to store the selection
                states.

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

        identifier = item.text(
            0
        )  # Assuming the first column text as a unique identifier
        states[identifier] = item.isSelected()
        for i in range(item.childCount()):
            child = item.child(i)
            self._store_item_selection_state(child, states)

    def _restore_selection_state_tree(
        self, tree_widget: QTreeWidget, states: dict
    ):
        """Restores the selection states of the tree widget items.

        Args:
            tree_widget (QTreeWidget): The tree widget to restore the selection
                states.
            states (dict): The dictionary containing the selection states of
                the items.
        """

        for i in range(tree_widget.topLevelItemCount()):
            item = tree_widget.topLevelItem(i)
            self._restore_item_selection_state(item, states)

    def _restore_item_selection_state(
        self, item: QTreeWidgetItem, states: dict
    ):
        """Restores the selection state of the item and its children.

        Args:
            item (QTreeWidgetItem): The item to restore the state.
            states (dict): The dictionary containing the states.
        """

        identifier = item.text(
            0
        )  # Assuming the first column text as a unique identifier
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

        selection_states = [
            item.isSelected() for item in range(list_widget.count())
        ]
        return selection_states

    def _restore_selection_state_list(
        self, list_widget: QListWidget, states: list
    ):
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
        # Sequence
        if entity_type == fxentities.entity.sequence and self.sequence:
            path = (
                Path(self._project_root)
                / "production"
                / "shots"
                / self.sequence
            )

        # Shot
        elif (
            entity_type == fxentities.entity.shot
            and self.sequence
            and self.shot
        ):
            path = (
                Path(self._project_root)
                / "production"
                / "shots"
                / self.sequence
                / self.shot
            )

        # Asset
        elif entity_type == fxentities.entity.asset and self.asset:
            path = (
                Path(self._project_root) / "production" / "assets" / self.asset
            )

        # Step
        elif (
            entity_type == fxentities.entity.step
            and self.sequence
            and self.shot
            and self.step
        ):
            path = (
                Path(self._project_root)
                / "production"
                / "shots"
                / self.sequence
                / self.shot
                / "workfiles"
                / self.step
            )

        # Task
        elif (
            entity_type == fxentities.entity.task
            and self.sequence
            and self.shot
            and self.step
            and self.task
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
            )

        # Workfile
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
        _path = str(
            path
        )  # ! Important to convert to str to retrieve the metadata
        _logger.debug(f"Displaying metadata for: {path.resolve().as_posix()}")
        metadata_data = fxfiles.get_all_metadata(_path)

        # Prepare the table
        table_widget = FXMetadataTableWidget()
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
            horizontal_header.model().setHeaderData(
                index, Qt.Horizontal, tooltip, Qt.ToolTipRole
            )
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
                value_item.setIcon(
                    fxicons.get_icon("font_download", color="#ffffff")
                )
            elif type == int:
                value_item = QTableWidgetItem(value)
                value_item.setIcon(
                    fxicons.get_icon("looks_one", color="#ffc107")
                )
            elif type == float:
                value_item = QTableWidgetItem(value)
                value_item.setIcon(
                    fxicons.get_icon("looks_two", color="#03a9f4")
                )
            elif type == dict:
                value_item = QTableWidgetItem(str(value))
                value_item.setIcon(fxicons.get_icon("book", color="#8bc34a"))
            elif type == list:
                value_item = QTableWidgetItem(str(value))
                value_item.setIcon(
                    fxicons.get_icon("view_list", color="#3f51b5")
                )
            else:
                value_item = QTableWidgetItem(value)
                value_item.setIcon(
                    fxicons.get_icon("font_download", color="#ffffff")
                )

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
            lambda: self._expand_all(self.tree_widget_shots),
        )
        action_collapse_all = fxguiutils.create_action(
            context_menu,
            "Collapse All",
            fxicons.get_icon("unfold_less"),
            lambda: self._collapse_all(self.tree_widget_shots),
        )
        action_show_in_file_browser = fxguiutils.create_action(
            context_menu,
            "Show in File Browser",
            fxicons.get_icon("open_in_new"),
            lambda: fxutils.open_directory(
                Path(self.tree_widget_shots.currentItem().data(1, Qt.UserRole))
                .parent.resolve()
                .as_posix()
                if self.tree_widget_shots.currentItem()
                else self._project_shots_path
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
            lambda: self._expand_all(self.tree_widget_assets),
        )
        action_collapse_all = fxguiutils.create_action(
            context_menu,
            "Collapse All",
            fxicons.get_icon("unfold_less"),
            lambda: self._collapse_all(self.tree_widget_assets),
        )
        action_show_in_file_browser = fxguiutils.create_action(
            context_menu,
            "Show in File Browser",
            fxicons.get_icon("open_in_new"),
            lambda: fxutils.open_directory(
                Path(
                    self.tree_widget_assets.currentItem().data(1, Qt.UserRole)
                )
                .parent.resolve()
                .as_posix()
                if self.tree_widget_assets.currentItem()
                else self._project_assets_path
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
            lambda: fxutils.open_directory(
                Path(self.list_steps.currentItem().data(Qt.UserRole + 1))
                .parent.resolve()
                .as_posix()
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
            lambda: fxutils.open_directory(
                Path(self.list_tasks.currentItem().data(Qt.UserRole + 1))
                .parent.resolve()
                .as_posix()
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

        # Create from current menu
        current_menu = context_menu.addMenu("New Version From Current")
        current_menu.setIcon(fxicons.get_icon("note_add"))
        if self.dcc == fxentities.DCC.standalone:
            current_menu.setEnabled(False)
        else:
            current_menu.setEnabled(True)

        # Create from preset menu
        preset_menu = context_menu.addMenu("New Version From Preset")
        preset_menu.setIcon(fxicons.get_icon("note_add"))

        # Define actions
        action_create_current_in_houdini = fxguiutils.create_action(
            current_menu,
            "Houdini",
            QIcon(
                str(
                    Path(fxenvironment._FQUINOX_IMAGES)
                    / "icons"
                    / "apps"
                    / "houdini.svg"
                )
            ),
            lambda: self.create_workfile_from_current(dcc=self.dcc),
        )

        action_show_in_file_browser = fxguiutils.create_action(
            context_menu,
            "Show in File Browser",
            fxicons.get_icon("open_in_new"),
            lambda: fxutils.open_directory(
                Path(
                    self.tree_widget_workfiles.currentItem().data(
                        1, Qt.UserRole
                    )
                )
                .parent.resolve()
                .as_posix()
                if self.tree_widget_workfiles.currentItem()
                else None
            ),
        )

        # Add workfile presets to the "Create from Preset" menu, adding an
        # action for each preset
        workfile_presets = (
            Path(self._project_root) / ".pipeline" / "workfile_presets"
        )
        for workfile_preset in workfile_presets.iterdir():
            if not workfile_preset.is_file():
                continue

            # Get the file extension to determine the type
            file_extension = workfile_preset.suffix.lstrip(".")

            # Skip files without or uncompatible extensions
            if file_extension in ["", "md"]:
                continue

            preset_name = workfile_preset.stem
            workfile_preset_path = (
                workfile_preset.resolve().absolute().as_posix()
            )

            preset_action = fxguiutils.create_action(
                preset_menu,
                preset_name,
                self._get_icon_based_on_type(file_extension),
                partial(
                    self.create_workfile_from_preset,
                    preset_file=workfile_preset_path,
                ),
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
        """Open a `FXCreateShotDialog` instance to create a new shot in the
        project.
        """

        widget = FXCreateShotDialog(
            parent=self,
            project_name=self._project_name,
            project_root=self._project_root,
            project_assets=self._project_assets_path,
            project_shots=self._project_shots_path,
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
        """Open a `FXCreateStepDialog` instance to create a new step in the
        shot.
        """
        if not self.sequence or not self.shot:
            warning = QMessageBox(self)
            warning.setWindowTitle("Create Step")
            warning.setText(
                f"You haven't selected a valid environment:<ul><li>Sequence: <b>{self.sequence}</b></li><li>Shot: <b>{self.shot}</b></li></ul>"
            )
            warning.setIcon(QMessageBox.Warning)
            warning.setStandardButtons(QMessageBox.Ok)
            warning.setTextInteractionFlags(
                Qt.TextSelectableByMouse
            )  # Make the text selectable
            warning.exec_()
            return

        widget = FXCreateStepDialog(
            parent=self,
            project_name=self._project_name,
            project_root=self._project_root,
            project_assets=self._project_assets_path,
            project_shots=self._project_shots_path,
            asset=self.asset,
            sequence=self.sequence,
            shot=self.shot,
        )
        widget.setWindowFlags(widget.windowFlags() | Qt.Window)
        widget.resize(400, 500)
        widget.show()

    # Tasks
    def create_task(self):
        """Open a `FXCreateTaskDialog` instance to create a new task in
        the step.
        """

        if not self.sequence or not self.shot or not self.step:
            warning = QMessageBox(self)
            warning.setWindowTitle("Create Task")
            warning.setText(
                f"You haven't selected a valid environment:<ul><li>Sequence: <b>{self.sequence}</b></li><li>Shot: <b>{self.shot}</b></li><li>Step: <b>{self.step}</b></ul>"
            )
            warning.setIcon(QMessageBox.Warning)
            warning.setStandardButtons(QMessageBox.Ok)
            warning.setTextInteractionFlags(
                Qt.TextSelectableByMouse
            )  # Make the text selectable
            warning.exec_()
            return

        widget = FXCreateTaskDialog(
            parent=self,
            project_name=self._project_name,
            project_root=self._project_root,
            project_assets=self._project_assets_path,
            project_shots=self._project_shots_path,
            asset=self.asset,
            sequence=self.sequence,
            shot=self.shot,
            step=self.step,
        )
        widget.setWindowFlags(widget.windowFlags() | Qt.Window)
        widget.resize(400, 500)
        widget.show()

    # Workfiles
    def create_workfile_from_current(self, dcc: str = fxentities.DCC.houdini):
        """Creates a workfile from the current file, inside the current
        `task/workfiles` directory.

        Args:
            dcc (str, optional): The DCC to create the workfile from.
                Defaults to `fxentities.DCC.houdini`.
        """

        if (
            not self.sequence
            or not self.shot
            or not self.step
            or not self.task
        ):
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

        # Get the current file path
        current_file_path = self.workfile_path
        workfile_dir = Path(current_file_path).parent.resolve().as_posix()

    def create_workfile_from_preset(self, preset_file: Optional[str] = None):
        """Creates a workfile from the selected preset file, inside
        the current `task/workfiles` directory.

        Args:
            preset_file (str, optional): The file to create the workfile from.
                Defaults to `None`.
        """

        if (
            not self.sequence
            or not self.shot
            or not self.step
            or not self.task
        ):
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

        _logger.debug(
            f"Old file path: '{preset_file_path.resolve().as_posix()}'"
        )
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
        fxfiles.set_multiple_metadata(
            new_file_path.resolve().as_posix(), metadata
        )

        self.refresh()

    # Common
    def _expand_all(self, tree_widget: QTreeWidget):
        """Expands all the items in the tree widget.

        Args:
            tree_widget (QTreeWidget): The tree widget to expand.
        """

        tree_widget.expandAll()

    def _collapse_all(self, tree_widget: QTreeWidget):
        """Collapses all the items in the tree widget.

        Args:
            tree_widget (QTreeWidget): The tree widget to collapse.
        """

        tree_widget.collapseAll()

    def closeEvent(self, _) -> None:
        """Overrides the close event to handle the system tray close event."""

        _logger.info(f"Closed")
        FXProjectBrowserWindow._instance = None
        self.setParent(None)


def run_project_browser(
    parent: Optional[QWidget] = None,
    quit_on_last_window_closed: bool = False,
    dcc: fxentities.DCC = fxentities.DCC.standalone,
) -> QMainWindow:
    """Runs the project browser UI.

    Args:
        parent (QWidget): The parent widget. Defaults to `None`.
        quit_on_last_window_closed (bool): Whether to quit the application when
            the last window is closed. Defaults to `False`.
        dcc (DCC): The DCC to use. Defaults to `None`.

    Returns:
        QMainWindow: The project browser window.
    """

    # Check if an instance is already open
    if FXProjectBrowserWindow._instance is not None:
        warning = FXDialog(parent, dialog_type="warning")
        warning.setWindowIcon(
            QIcon(
                str(
                    Path(fxenvironment._FQUINOX_IMAGES)
                    / "fxquinox_logo_background_dark.svg"
                )
            )
        )
        warning.setWindowTitle(f"Project Browser Already Running")
        warning.set_message(
            f"The Project Browser is already running.<br><br>"
            f"Close the existing Project Browser before starting a new one."
        )
        warning.set_details(str(FXProjectBrowserWindow._instance))
        warning.exec_()
        _logger.warning("Project Browser already running")
        return FXProjectBrowserWindow._instance

    # Application
    if not parent:
        _fix = QUiLoader()  # XXX: This is a PySide6 bug
        app = fxwidgets.FXApplication.instance()
        app.setQuitOnLastWindowClosed(quit_on_last_window_closed)

    # Get current project
    project_info = fxcore.get_project()
    project_name = project_info.get("FXQUINOX_PROJECT_NAME", None)

    ui_file = Path(fxenvironment._FXQUINOX_UI) / "project_browser.ui"
    icon_path = (
        Path(fxenvironment._FQUINOX_IMAGES)
        / "fxquinox_logo_background_light.svg"
    )

    window = FXProjectBrowserWindow(
        parent=parent if isinstance(parent, QWidget) else None,
        icon=icon_path.resolve().as_posix(),
        title="Project Browser",
        size=(2000, 1200),
        project=project_name,
        version="0.0.1",
        company="fxquinox",
        ui_file=ui_file.resolve().as_posix(),
        project_info=project_info,
        dcc=dcc,
    )
    window.show()
    # window.setStyleSheet(fxstyle.load_stylesheet())

    if not parent:
        app.exec_()

    return window


if __name__ == "__main__":
    run_project_browser(
        parent=None,
        quit_on_last_window_closed=True,
        dcc=fxentities.DCC.standalone,
    )
