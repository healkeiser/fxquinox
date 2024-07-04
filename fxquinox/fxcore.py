"""The fxcore module provides a set of tools for managing and automating
the creation of VFX entities.
"""

# Built-in
from functools import lru_cache
import json
import os
from pathlib import Path
from turtle import color
from git import refresh
import psutil
import sys
import subprocess
import textwrap
from typing import Dict, Optional, Tuple

# Third-party
from fxgui import fxwidgets, fxicons, fxstyle, fxutils as fxguiutils
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *
import yaml

# Internal
from fxquinox import fxenvironment, fxlog, fxfiles
import fxquinox


# Log
_logger = fxlog.get_logger("fxquinox.fxcore")
_logger.setLevel(fxlog.DEBUG)

# Globals
_PROJECT = "project"
_SEQUENCE = "sequence"
_SHOTS_DIR = "shots"
_SHOT = "shot"
_ASSETS_DIR = "assets"
_ASSET = "asset"
_STEP = "step"
_TASK = "task"
_WORKFILE = "workfile"


@lru_cache(maxsize=None)
def _get_structure_dict(entity: str, file_type: str = "yaml") -> Dict:
    """Reads the project structure from the JSON or YAML file and returns it.

    Args:
        entity (str): The entity type for which the structure is needed.
        file_type (str): The type of file to read the structure from.
            Can be either "json" or "yaml". Defaults to "yaml".

    Returns:
        dict: The project structure dictionary.

    Raises:
        FileNotFoundError: If the structure file is not found.

    Note:
        This function is decorated with `lru_cache` to avoid reading the file
        every time.
    """

    structure_path = Path(__file__).parent / "structures" / f"{entity}_structure.{file_type}"
    if structure_path.exists():
        if file_type == "yaml":
            return yaml.safe_load(structure_path.read_text())
        return json.loads(structure_path.read_text())
    else:
        error_message = f"Structure file '{structure_path}' not found"
        _logger.error(error_message)
        raise FileNotFoundError(error_message)


def _create_entity(entity_type: str, entity_name: str, base_dir: str = ".", parent: QWidget = None) -> Optional[str]:
    """Generic function to create a new directory for a given entity type in
    the specified base directory.

    Args:
        entity_type (str): The type of entity to create.
        entity_name (str): The name of the entity to create.
        base_dir (str): The base directory in which to create the entity.
            Defaults to the current directory.
        parent (QWidget): The parent widget for the message box.

    Returns:
        Optional[str]: The name of the entity if created, `None` otherwise.
    """

    base_dir_path = Path(base_dir)
    entity_dir = base_dir_path / entity_name

    structure_dict = _get_structure_dict(entity_type)
    structure_dict = fxfiles.replace_placeholders_in_dict(
        structure_dict,
        {
            entity_type.upper(): entity_name,
            f"{entity_type.upper()}_ROOT": entity_dir.resolve().as_posix(),
        },
    )

    _base_dir_path = base_dir_path.resolve().as_posix()

    if Path(entity_dir).exists():
        if parent:
            confirmation = QMessageBox.question(
                parent,
                f"Create {entity_type.capitalize()}",
                f"There's already a {entity_type} '{entity_name}' in '{_base_dir_path}', do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if confirmation == QMessageBox.No:
                _logger.info(f"{entity_type.capitalize()} creation cancelled")
                return None
        else:
            while True:
                confirmation = input(
                    f"There's already a {entity_type} '{entity_name}' in "
                    f"'{_base_dir_path}', do you want to continue? (y/n): "
                )
                if confirmation.lower() == "y":
                    break
                elif confirmation.lower() == "n":
                    _logger.info(f"{entity_type.capitalize()} creation cancelled")
                    return None
                else:
                    _logger.warning("Please enter 'y' to continue or 'n' to cancel")

    fxfiles.create_structure_from_dict(structure_dict, _base_dir_path)
    _logger.info(f"{entity_type.capitalize()} '{entity_name}' created in '{_base_dir_path}'")
    return entity_name


def _check_entity(entity_type: str, entity_path: str = ".") -> bool:
    """Checks if the given folder of file has the correct entity type by
    checking its metadata.

    Args:
        entity_type (str): The type of entity to check.
        entity_path (str): The entity path. Defaults to the current directory.

    Returns:
        bool: `True` if the entity is valid, `False` otherwise.
    """

    entity_path = Path(entity_path).resolve().as_posix()
    metadata_creator = fxfiles.get_metadata(entity_path, "creator")
    metadata_entity = fxfiles.get_metadata(entity_path, "entity")
    _logger.debug(f"Directory: '{entity_path}'")
    _logger.debug(f"Metadata creator: '{metadata_creator}'")
    _logger.debug(f"Metadata entity: '{metadata_entity}'")

    if metadata_creator == "fxquinox" and metadata_entity == entity_type:
        return True
    return False


###### Projects


class InvalidProjectError(Exception):
    """Exception raised when a project is not valid."""

    pass


def create_project(project_name: str, base_dir: str = ".") -> Optional[str]:
    """Creates a new project directory structure.

    Args:
        project_name (str): The name of the project to create.
        base_dir (str): The base directory where the project will be created.
            Defaults to the current directory.

    Returns:
        Optional[str]: The name of the project if created, `None` otherwise.

    Examples:
        Python
        >>> create_project("my_project")

        CLI
        >>> python -m fxquinox.cli.fxcore create_project my_project
    """

    return _create_entity(_PROJECT, project_name, base_dir)


def check_project(base_dir: str = ".") -> bool:
    """Checks if a valid project directory structure exists.

    Args:
        base_dir (str): The base directory where the project should be located.
            Defaults to the current directory.

    Returns:
        bool: `True` if the project is valid, `False` otherwise.
    """

    return _check_entity(_PROJECT, base_dir)


###### Sequences


class InvalidSequenceError(Exception):
    """Exception raised when a sequence is not valid."""

    pass


class InvalidSequencesDirectoryError(Exception):
    """Exception raised when a sequences directory is not valid."""

    pass


def create_sequence(sequence_name: str, base_dir: str = ".") -> Optional[str]:
    """Creates a new sequence directory structure within a project.

    Args:
        sequence_name (str): The name of the sequence to create.
        base_dir (str): The base directory where the sequence will be created,
            typically the "project/production/shots" directory.
            Defaults to the current directory.

    Returns:
        Optional[str]: The name of the sequence if created, `None` otherwise.

    Examples:
        Python
        >>> create_sequence("010", "/path/to/shots")

        CLI
        >>> fxquinox.cli.fxcore.create_sequence 010 --base_dir "/path/to/shots"
    """

    # Ensure right naming convention
    if len(sequence_name) != 3:
        error_message = "Sequence names should be exactly 3 characters long"
        _logger.error(error_message)
        raise ValueError(error_message)

    # Check the parent entity sequence "shots" directory validity before
    # creating the sequence
    base_dir_path = Path(base_dir).resolve()

    if not _check_shots_directory(base_dir_path):
        error_message = f"'{base_dir_path.as_posix()}' is not a valid shots directory"
        _logger.error(error_message)
        raise InvalidSequencesDirectoryError(error_message)

    # Create the sequence
    return _create_entity(_SEQUENCE, sequence_name, base_dir_path)


def create_sequences(sequence_names: list[str], base_dir: str = ".") -> Optional[list[str]]:
    """Creates new sequence directory structures within a project.

    Args:
        sequence_names (list): The names of the sequences to create.
        base_dir (str): The base directory where the sequence will be created,
            typically the "project/production/shots" directory.
            Defaults to the current directory.

    Returns:
        Optional[list]: The names of the sequences if created, `None` otherwise.

    Examples:
        Python
        >>> create_sequences(["010", "020"], "/path/to/shots")

        CLI
        >>> fxquinox.cli.fxcore.create_sequences 010,020 --base_dir "/path/to/shots"
    """

    # Check the parent entity sequence "shots" directory validity before
    # creating the sequence
    base_dir_path = Path(base_dir).resolve()

    if not _check_shots_directory(base_dir_path):
        error_message = f"'{base_dir_path}' is not a valid shots directory"
        _logger.error(error_message)
        raise InvalidSequencesDirectoryError(error_message)

    # Create the sequences
    sequences = []
    for sequence_name in sequence_names:
        _create_entity(_SEQUENCE, sequence_name, base_dir_path)
        sequences.append(sequence_name)

    return sequences


def check_sequence(base_dir: str = ".") -> bool:
    """Checks if a valid sequence directory structure exists within a project.

    Args:
        base_dir (str): The base directory where the sequence should be located,
            typically the "project/production/shots" directory.
            Defaults to the current directory.

    Returns:
        bool: `True` if the sequence is valid, `False` otherwise.
    """

    return _check_entity(_SEQUENCE, base_dir)


# ? It could appear as this function should be in the shots section, but it's
# ? here because the `shots` directory is the one holding the sequences.
def _check_shots_directory(base_dir: str = ".") -> bool:
    """Checks if a valid "shots" (which holds the sequences) directory
    structure exists within a project.

    Args:
        base_dir (str): The base directory where the "shots" directory should
            be located, typically the "project/production" directory.
            Defaults to the current directory.

    Returns:
        bool: `True` if the shots directory is valid, `False` otherwise.
    """

    return _check_entity(_SHOTS_DIR, base_dir)


###### Shots


class InvalidShotError(Exception):
    """Exception raised when a shot is not valid."""

    pass


def create_shot(shot_name: str, base_dir: str = ".", parent: QWidget = None) -> Optional[str]:
    """Creates a new shot directory structure within a sequence.

    Args:
        shot_name (str): The name of the shot to create.
        base_dir (str): The base directory where the shot will be created,
            typically the "project/production/shots/sequence" directory.
            Defaults to the current directory.
        parent (QWidget): The parent widget for the message box. Only
            applicable in a GUI environment.

    Returns:
        Optional[str]: The name of the shot if created, `None` otherwise.

    Examples:
        Python
        >>> create_shot("0010", "/path/to/sequence")

        CLI
        >>> fxquinox.cli.fxcore.create_shot 0010 --base_dir "/path/to/sequence"
    """

    # Ensure right naming convention
    if len(shot_name) != 4:
        error_message = "Shot names should be exactly 4 characters long"
        _logger.error(error_message)
        raise ValueError(error_message)

    # Check the parent entity sequence validity before creating the shot
    base_dir_path = Path(base_dir).resolve()
    sequence_name = base_dir_path.name

    if not check_sequence(base_dir_path):
        error_message = f"'{sequence_name}' in '{base_dir_path.as_posix()}' is not a sequence"
        _logger.error(error_message)
        raise InvalidSequenceError(error_message)

    # Create the shot
    return _create_entity(_SHOT, shot_name, base_dir_path, parent)


def create_shots(shot_names: list[str], base_dir: str = ".") -> Optional[list[str]]:
    """Creates new shot directory structures within a sequence.

    Args:
        shot_names (list[str]): The names of the shots to create.
        base_dir (str): The base directory where the shots will be created,
            typically the "project/production/shots/sequence" directory.
            Defaults to the current directory.

    Returns:
        Optional[list[str]]: The names of the shots if created,
            `None` otherwise.

    Examples:
        Python
        >>> create_shots(["0010", "0020"], "/path/to/sequence")

        CLI
        >>> fxquinox.cli.fxcore.create_shots 0010,0020 --base_dir "/path/to/sequence"
    """

    # Check the parent entity sequence validity before creating the shot
    base_dir_path = Path(base_dir).resolve()
    sequence_name = base_dir_path.name

    if not check_sequence(base_dir_path):
        error_message = f"'{sequence_name}' in '{base_dir_path.as_posix()}' is not a sequence"
        _logger.error(error_message)
        raise InvalidSequenceError(error_message)

    # Proceed to create each shot if the sequence is valid
    shots = []
    for shot_name in shot_names:
        # Ensure right naming convention
        if len(shot_name) != 4:
            error_message = "Shot names should be exactly 4 characters long"
            _logger.error(error_message)
            raise ValueError(error_message)

        _create_entity(_SHOT, shot_name, base_dir_path)
        shots.append(shot_name)

    return shots


def check_shot(base_dir: str = ".") -> bool:
    """Checks if a valid shot directory structure exists within a sequence.

    Args:
        base_dir (str): The base directory where the shot should be located,
            typically the "project/production/shots/sequence" directory.
            Defaults to the current directory.

    Returns:
        bool: `True` if the shot is valid, `False` otherwise.
    """

    return _check_entity(_SHOT, base_dir)


###### Assets


class InvalidAssetError(Exception):
    """Exception raised when an asset is not valid."""

    pass


class InvalidAssetsDirectoryError(Exception):
    """Exception raised when an assets directory is not valid."""

    pass


def create_asset(asset_name: str, base_dir: str = ".") -> Optional[str]:
    """Creates a new asset directory structure within a project.

    Args:
        asset_name (str): The name of the asset to create.
        base_dir (str): The base directory where the asset will be created,
            typically the "project/production/assets" directory.
            Defaults to the current directory.

    Returns:
        Optional[str]: The name of the asset if created, `None` otherwise.

    Examples:
        Python
        >>> create_asset("charA", "/path/to/assets")

        CLI
        >>> fxquinox.cli.fxcore.create_asset charA --base_dir "/path/to/assets"
    """

    # Check the parent entity assets "assets" directory validity before
    # creating the asset
    base_dir_path = Path(base_dir).resolve()

    if not _check_assets_directory(base_dir_path):
        error_message = f"'{base_dir_path.as_posix()}' is not a valid assets directory"
        _logger.error(error_message)
        raise InvalidAssetsDirectoryError(error_message)

    # Create the asset
    return _create_entity(_ASSET, asset_name, base_dir)


def create_assets(asset_names: list[str], base_dir: str = ".") -> Optional[list[str]]:
    """Creates new asset directory structures within a project.

    Args:
        asset_names (list): The names of the assets to create.
        base_dir (str): The base directory where the asset will be created,
            typically the "project/production/assets" directory.
            Defaults to the current directory.

    Returns:
        Optional[list]: The names of the assets if created, `None` otherwise.

    Examples:
        Python
        >>> create_assets(["charA", "propA"], "/path/to/assets")

        CLI
        >>> fxquinox.cli.fxcore.create_assets charA,propA --base_dir "/path/to/assets"
    """

    # Check the parent entity sequence validity before creating the shot
    base_dir_path = Path(base_dir).resolve()

    if not _check_assets_directory(base_dir_path):
        error_message = f"'{base_dir_path.as_posix()}' is not a valid assets directory"
        _logger.error(error_message)
        raise InvalidAssetsDirectoryError(error_message)

    # Create the assets
    assets = []
    for asset_name in asset_names:
        _create_entity(_ASSET, asset_name, base_dir_path)
        assets.append(asset_name)

    return assets


def check_asset(base_dir: str = ".") -> bool:
    """Checks if a valid asset directory structure exists within a project.

    Args:
        base_dir (str): The base directory where the asset should be located,
            typically the "project/production/assets" directory.
            Defaults to the current directory.

    Returns:
        bool: `True` if the asset is valid, `False` otherwise.
    """

    return _check_entity(_ASSET, base_dir)


def _check_assets_directory(base_dir: str = ".") -> bool:
    """Checks if a valid "assets" (which holds the assets) directory
    structure exists within a project.

    Args:
        base_dir (str): The base directory where the "assets" directory should
            be located, typically the "project/production" directory.
            Defaults to the current directory.

    Returns:
        bool: `True` if the assets directory is valid, `False` otherwise.
    """

    return _check_entity(_ASSETS_DIR, base_dir)


###### Steps (departments)
# TODO: Implement the steps


class InvalidStepError(Exception):
    """Exception raised when a step is not valid."""

    pass


def create_step(step_name: str, base_dir: str = ".") -> Optional[str]:
    base_dir_path = Path(base_dir).resolve()

    if not check_workfile(base_dir_path):
        error_message = f"'{base_dir_path.as_posix()}' is not a valid workfiles directory"
        _logger.error(error_message)
        raise InvalidStepError(error_message)

    # Create the step
    return _create_entity(_STEP, step_name, base_dir_path)


def check_step(base_dir: str = ".") -> bool:
    """Checks if a valid step directory structure exists within a project.

    Args:
        base_dir (str): The base directory where the step should be located,
            typically the "project/production/steps" directory.
            Defaults to the current directory.

    Returns:
        bool: `True` if the step is valid, `False` otherwise.
    """

    return _check_entity(_STEP, base_dir)


###### Tasks
# TODO: Implement the tasks


class InvalidTaskError(Exception):
    """Exception raised when a task is not valid."""

    pass


def create_task(task_name: str, base_dir: str = ".") -> Optional[str]:
    base_dir_path = Path(base_dir).resolve()

    if not check_step(base_dir_path):
        error_message = f"'{base_dir_path.as_posix()}' is not a valid steps directory"
        _logger.error(error_message)
        raise InvalidTaskError(error_message)

    # Create the task
    return _create_entity(_TASK, task_name, base_dir_path)


###### Workfiles


def check_workfile(base_dir: str = ".") -> bool:
    """Checks if a valid workfile directory structure exists within a project.

    Args:
        base_dir (str): The base directory where the workfile should be located,
            typically the "project/production/workfiles" directory.
            Defaults to the current directory.

    Returns:
        bool: `True` if the workfile is valid, `False` otherwise.
    """

    return _check_entity(_WORKFILE, base_dir)


###### UI


class _FXTempWidget(QWidget):
    """A temporary widget that will be linked to display the splashscreen, as
    we can't `splashcreen.finish()` without a QWidget."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGeometry(0, 0, 0, 0)
        self.hide()
        self.close()


class FXExecutableRunnerThread(QThread):
    """A QThread subclass to run an executable in a separate thread."""

    # Define a signal to emit upon completion, if needed
    finished = Signal()

    def __init__(self, executable, commands=None, parent=None):
        super(FXExecutableRunnerThread, self).__init__(parent)
        self.executable = executable
        self.commands = commands

    def run(self):
        if self.executable:
            call = ['"' + self.executable + '"'] + self.commands if self.commands else ['"' + self.executable + '"']
        else:
            # If executable is empty, ensure commands is not `None` or empty
            # before proceeding
            if self.commands:
                call = self.commands
            else:
                _logger.error("No executable or commands provided to run")
                self.finished.emit()
                return

        _logger.debug(f"Call: {call}")

        if sys.platform == "win32":
            # On Windows, use `start cmd.exe /k` to open a new command prompt
            # that stays open
            cmd = "start cmd.exe /k " + " ".join(call)
            subprocess.Popen(cmd, shell=True)
        else:
            # On Unix-like systems, we might need to specify a terminal
            # emulator.
            # For example, using `xterm`:
            # >>> cmd = ["xterm", "-e"] + call
            # >>> subprocess.Popen(cmd)
            # Or we can simply run the command in a new shell without keeping
            # the terminal open:
            _logger.debug(f"Call: {call}")
            subprocess.Popen(call, shell=True)

        self.finished.emit()


class FXLauncherSystemTray(fxwidgets.FXSystemTray):
    """The Fxuinox main launcher UI class.

    Args:
        parent (QWidget): The parent widget.
        icon (QIcon): The icon to display in the system tray.
        project (str): The current project name.

    Signals:
        project_changed (str, str): The signal emitted when the project is
            changed.

    Note:
        This class inherits from `FXSystemTray` which is a custom system tray
        class that inherits from `QSystemTrayIcon`.
    """

    project_changed = Signal(str, str)

    def __init__(self, parent=None, icon=None, project=None):
        super().__init__(parent, icon)

        # Attributes
        self.project = project

        _logger.debug(f"Launcher project: '{self.project}'")

        self.colors = fxstyle.load_colors_from_jsonc()
        self.runner_threads = []

        # Methods
        self.__create_actions()
        self._create_label()
        self._create_app_launcher(project_name=self.project)
        self.__handle_connections()
        self._update_label(project_name=self.project)
        self._toggle_action_state(project_name=self.project)

    def __handle_connections(self) -> None:
        """Connects the signals to the slots."""

        self.project_changed.connect(self._update_label)
        self.project_changed.connect(self._toggle_action_state)
        self.project_changed.connect(self._load_and_display_apps)

    def __create_actions(self) -> None:
        """Creates the actions for the system tray."""

        self.create_project_action = fxguiutils.create_action(
            self.tray_menu,
            "Create Project...",
            fxicons.get_icon("movie_filter"),
            lambda: set_project(launcher=self),
        )

        self.set_project_action = fxguiutils.create_action(
            self.tray_menu,
            "Set Project",
            fxicons.get_icon("movie"),
            lambda: set_project(launcher=self),
        )

        self.open_project_browser_action = fxguiutils.create_action(
            self.tray_menu,
            "Project Browser...",
            fxicons.get_icon("perm_media"),
            run_project_browser,
        )

        self.open_project_directory_action = fxguiutils.create_action(
            self.tray_menu,
            "Open Project Directory...",
            fxicons.get_icon("open_in_new"),
            open_project_directory,
        )

        #
        self.fxquinox_menu = QMenu("Fxquinox", self.tray_menu)
        self.fxquinox_menu.setIcon(QIcon(str(Path(__file__).parents[1] / "images" / "fxquinox_logo_light.svg")))

        self.open_fxquinox_appdata = fxguiutils.create_action(
            self.fxquinox_menu,
            "Open Application Data Directory...",
            fxicons.get_icon("open_in_new"),
            lambda: open_directory(fxenvironment.FXQUINOX_APPDATA),
        )

        self.open_fxquinox_temp = fxguiutils.create_action(
            self.fxquinox_menu,
            "Open Temp Directory...",
            fxicons.get_icon("open_in_new"),
            lambda: open_directory(fxenvironment.FXQUINOX_TEMP),
        )

        self.tray_menu.insertAction(self.quit_action, self.open_project_directory_action)
        self.tray_menu.insertAction(self.open_project_directory_action, self.open_project_browser_action)
        self.tray_menu.insertAction(self.open_project_browser_action, self.set_project_action)

        self.tray_menu.insertMenu(self.quit_action, self.fxquinox_menu)
        self.fxquinox_menu.addAction(self.open_fxquinox_appdata)
        self.fxquinox_menu.addAction(self.open_fxquinox_temp)

        self.tray_menu.insertSeparator(self.open_project_directory_action)
        self.tray_menu.insertSeparator(self.quit_action)

    def _create_label(self) -> None:
        """Creates the label for the system tray."""

        container_widget = QWidget()
        layout = QVBoxLayout(container_widget)
        self.label = QLabel(self.project)
        layout.addWidget(self.label)
        layout.setContentsMargins(10, 10, 10, 10)
        label_action = QWidgetAction(self.tray_menu)
        label_action.setDefaultWidget(container_widget)
        self.tray_menu.insertAction(self.set_project_action, label_action)
        self._set_label_style()

    def _create_app_launcher(self, project_root: str = None, project_name: str = None) -> None:
        """Creates the application launcher as a grid and adds a QLineEdit for additional arguments."""
        container_widget = QWidget()
        container_widget.setObjectName("app_launcher_container")
        container_widget.setStyleSheet(
            "#app_launcher_container { background-color: #131212; border-top: 1px solid #424242; border-bottom: 1px solid #424242}"
        )
        layout = QVBoxLayout(container_widget)  # Use QVBoxLayout to stack grid and line edit
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Grid layout for apps
        self.grid_layout = QGridLayout()
        layout.addLayout(self.grid_layout)

        # Container for the line edit and clear button
        args_layout = QHBoxLayout()

        # Line edit for additional arguments
        self.additional_args_line_edit = QLineEdit()
        self.additional_args_line_edit.setPlaceholderText("Additional arguments...")
        args_layout.addWidget(self.additional_args_line_edit)

        # Clear button for the line edit
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.additional_args_line_edit.clear)
        args_layout.addWidget(clear_button)
        layout.addLayout(args_layout)

        # Add the container widget to the tray menu
        self.list_apps_action = QWidgetAction(self.tray_menu)
        self.list_apps_action.setDefaultWidget(container_widget)
        self.tray_menu.insertAction(self.open_project_browser_action, self.list_apps_action)

        # Load apps
        self._load_and_display_apps(project_root, project_name)

    def _load_and_display_apps(self, project_root: str = None, project_name: str = None) -> None:
        # Clear existing widgets from the grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            self.grid_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

        # Load apps from YAML file
        project_info = get_project()
        project_root = project_info.get("FXQUINOX_PROJECT_ROOT", None)
        apps_config_path = Path(project_root) / ".pipeline" / "project_config" / "apps.yaml"
        if not apps_config_path.exists():
            return
        apps_config = yaml.safe_load(apps_config_path.read_text())

        # Parse the `apps.yaml` file and add buttons for each app found
        row, col = 0, 0
        button_size = QSize(64, 64)

        for app_info in apps_config["apps"]:
            for app, details in app_info.items():
                version = details.get("version", {})
                version_major = version.get("major", 0)
                version_minor = version.get("minor", 0)
                version_patch = version.get("patch", 0)
                executable = (
                    details.get("executable", "")
                    .replace("$VERSION_MAJOR$", str(version_major))
                    .replace("$VERSION_MINOR$", str(version_minor))
                    .replace("$VERSION_PATCH$", str(version_patch))
                )
                commands = details.get("commands", [])
                icon_file = details.get("icon", "").replace("$FXQUINOX_ROOT$", fxenvironment.FXQUINOX_ROOT)

                # Create the button
                button = QPushButton()
                button.setIcon(QIcon(str(icon_file)))
                button.setIconSize(QSize(48, 48))
                button.setFixedSize(button_size)
                button.clicked.connect(lambda exe=executable, cmds=commands: self._launch_executable(exe, cmds))
                # Tooltip
                version_string = (
                    (
                        f"<b>Version</b>: {version_major if version_major else ''}"
                        f"{f'.{version_minor}' if version_minor else ''}"
                        f"{f'.{version_patch}' if version_patch else ''}<br><br>"
                    )
                    if version_major or version_minor or version_patch
                    else "<b>Version</b>: None<br><br>"
                )
                tooltip = (
                    f"{version_string}"
                    f"<b>Executable</b>: {executable if executable else None}<br><br>"
                    f"<b>Commands</b>: <code>{commands if commands else None}</code>"
                )
                fxguiutils.set_formatted_tooltip(button, app.capitalize(), tooltip)
                # Add the button to the grid layout
                self.grid_layout.addWidget(button, row, col)
                col += 1
                if col >= 4:
                    row += 1
                    col = 0

    def _launch_executable(self, executable: str, commands: list = None) -> None:
        """Launches the given executable, with optional commands.

        Args:
            executable (str): The path to the executable to launch.
            commands (list): The list of commands to pass to the executable.
        """

        additional_args = self.additional_args_line_edit.text().strip().split()
        if commands is None:
            commands = additional_args
        else:
            commands.extend(additional_args)

        runner_thread = FXExecutableRunnerThread(executable, commands)
        self.runner_threads.append(runner_thread)
        # Delete thread on completion
        runner_thread.finished.connect(lambda rt=runner_thread: self._on_thread_finished(rt))
        runner_thread.start()

    def _on_thread_finished(self, thread: FXExecutableRunnerThread) -> None:
        """Slot to handle thread finished signal. Attempt to remove the thread
        from the tracking list.

        Args:
            thread (FXExecutableRunnerThread): The thread that has finished.
        """

        thread.wait()  # Optional: Wait for the thread to fully finish if needed
        if thread in self.runner_threads:
            self.runner_threads.remove(thread)
        else:
            _logger.debug(f"Thread not found in list: '{thread}'")
        _logger.debug(f"Thread finished: '{thread}'")

    def _update_label(self, project_root: str = None, project_name: str = None) -> None:
        """Updates the label text with the current project name."""

        self.label.setText(project_name or "No project set")
        self._set_label_style(project_root, project_name)

    def _set_label_style(self, project_root: str = None, project_name: str = None) -> None:
        """Sets the label stylesheet based on the current project status."""

        if project_name:
            color = self.colors["feedback"]["success"]["light"]
        else:
            color = self.colors["feedback"]["warning"]["light"]
        self.label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12pt;")

    def _toggle_action_state(self, project_root: str = None, project_name: str = None) -> None:
        """Toggles the state of the actions based on the project status."""

        if project_name:
            self.open_project_browser_action.setEnabled(True)
            self.open_project_directory_action.setEnabled(True)
            self.list_apps_action.setEnabled(True)
        else:
            self.open_project_browser_action.setEnabled(False)
            self.open_project_directory_action.setEnabled(False)
            self.list_apps_action.setEnabled(False)

    def closeEvent(self, event) -> None:
        """Overrides the close event to handle the system tray close event."""

        _logger.info(f"Closed")
        self.setParent(None)
        _remove_lock(Path(fxenvironment.FXQUINOX_TEMP) / "launcher.lock")
        fxwidgets.FXApplication.instance().quit()
        QApplication.instance().quit()


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
        accent_color: str = "#039492",
        ui_file: Optional[str] = None,
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
            accent_color,
            ui_file,
        )

        # Methods
        self._get_project()
        self._rename_ui()
        self._create_icons()
        self._modify_ui()
        self._populate_assets()
        self._populate_shots()
        self._handle_connections()

        self.statusBar().showMessage("Initialized project browser", self.INFO, logger=_logger)

    def _get_project(self) -> None:
        """_summary_

        Returns:
            dict: _description_
        """

        self.project_info = get_project()
        self._project_root = self.project_info.get("FXQUINOX_PROJECT_ROOT", None)
        self._project_name = self.project_info.get("FXQUINOX_PROJECT_NAME", None)
        self._project_assets = self.project_info.get("FXQUINOX_PROJECT_ASSETS", None)
        self._project_shots = self.project_info.get("FXQUINOX_PROJECT_SHOTS", None)

    def _rename_ui(self):
        """_summary_"""

        self.label_project = self.ui.label_project
        self.line_project = self.ui.line_project
        #
        self.tab_assets_shots = self.ui.tab_assets_shots
        self.tab_assets = self.ui.tab_assets
        self.label_icon_filter_assets = self.ui.label_icon_filter_assets
        self.line_edit_filter_assets = self.ui.frame_filter_assets
        self.tree_widget_assets = self.ui.tree_widget_assets
        #
        self.tab_shots = self.ui.tab_shots
        self.label_icon_filter_shots = self.ui.label_icon_filter_shots
        self.line_edit_filter_shots = self.ui.line_edit_filter_shots
        self.tree_widget_shots = self.ui.tree_widget_shots
        #
        self.group_box_steps = self.ui.group_box_steps
        self.list_steps = self.ui.list_steps
        #
        self.group_box_tasks = self.ui.group_box_tasks
        self.list_tasks = self.ui.list_tasks

    def _handle_connections(self):
        # Assets
        self.tree_widget_assets.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget_assets.customContextMenuRequested.connect(self._on_assets_context_menu)

        # Shots
        self.tree_widget_shots.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget_shots.customContextMenuRequested.connect(self._on_shots_context_menu)

        # Steps
        self.list_steps.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_steps.customContextMenuRequested.connect(self._on_steps_context_menu)

        # Tasks
        # self.list_tasks.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.list_tasks.customContextMenuRequested.connect(self._on_tasks_context_menu)

    def _create_icons(self):
        """_summary_"""

        self.icon_search = fxicons.get_pixmap("search", 18)

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

    #
    def refresh(self):
        self._populate_shots()

    def _populate_shots(self) -> None:
        """Populates the shots tree widget with the shots in the project."""

        # Check if the project root is set
        if not self._project_root:
            return

        # Check if the shots directory exists
        shots_dir = Path(self._project_root) / "production" / "shots"
        if not shots_dir.exists():
            return

        # Iterate over the sequences and shots
        icon_sequence = fxicons.get_pixmap("camera_roll")
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
            sequence_item.setData(0, Qt.UserRole, sequence_path)
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
                shot_item.setData(0, Qt.UserRole, shot_path)
                shot_item.setToolTip(
                    0,
                    f"<b>{shot.name}</b><hr><b>Entity</b>: Shot<br><br><b>Path</b>: {shot_path}",
                )

    def _populate_assets(self) -> None:
        """Populates the assets tree widget with the assets in the project."""

        # Check if the project root is set
        if not self._project_root:
            return

        # Check if the assets directory exists
        assets_dir = Path(self._project_root) / "production" / "assets"
        if not assets_dir.exists():
            return

        # Iterate over the assets
        icon_asset = fxicons.get_pixmap("view_in_ar")

        for asset in assets_dir.iterdir():
            if not asset.is_dir():
                continue

            asset_item = QTreeWidgetItem(self.tree_widget_assets)
            asset_item.setText(0, asset.name)
            asset_item.setIcon(0, icon_asset)

    # ' Contextual menus
    # Shots
    def _on_shots_context_menu(self, point: QPoint):
        # Create the context menu
        context_menu = QMenu(self)

        # Define actions
        action_create_shot = fxguiutils.create_action(
            context_menu,
            "Create Shot",
            fxicons.get_icon("image"),
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
        ection_expand_all = fxguiutils.create_action(
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
            lambda: self.show_in_file_browser(
                self.tree_widget_shots.currentItem().data(0, Qt.UserRole)
                if self.tree_widget_shots.currentItem()
                else get_project().get("FXQUINOX_PROJECT_SHOTS", None)
            ),
        )

        # Add actions to the context menu
        context_menu.addAction(action_create_shot)
        context_menu.addSeparator()
        context_menu.addAction(action_edit_shot)
        context_menu.addAction(action_delete_shot)
        context_menu.addSeparator()
        context_menu.addAction(ection_expand_all)
        context_menu.addAction(action_collapse_all)
        context_menu.addAction(action_show_in_file_browser)

        # Show the context menu
        context_menu.exec_(self.tree_widget_shots.mapToGlobal(point))

    # Assets
    def _on_assets_context_menu(self, point: QPoint):
        # Similar to on_shots_context_menu, but for assets
        context_menu = QMenu(self)

        # Define actions

        action_edit_asset = QAction("Edit Asset", self)
        action_delete_asset = QAction("Delete Asset", self)

        # Add actions to the context menu
        context_menu.addAction(action_edit_asset)
        context_menu.addAction(action_delete_asset)

        # Connect actions to slots
        action_edit_asset.triggered.connect(self.edit_asset)
        action_delete_asset.triggered.connect(self.delete_asset)

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

        # Add actions to the context menu
        context_menu.addAction(action_create_step)

        # Connect actions to slots

        # Show the context menu
        context_menu.exec_(self.list_steps.mapToGlobal(point))

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
        widget = FXCreateShotWidget(
            parent=self,
            project_name=self._project_name,
            project_root=self._project_root,
            project_assets=self._project_assets,
            project_shots=self._project_shots,
        )
        widget.setWindowFlags(widget.windowFlags() | Qt.Window)
        widget.resize(400, 200)
        widget.show()

        self.refresh()

    def edit_shot(self):
        # Implement shot editing logic here
        pass

    def delete_shot(self):
        # Implement shot deletion logic here
        pass

    # Steps
    def create_step(self):
        widget = FXCreateStepWidget(
            parent=self,
            project_name=self._project_name,
            project_root=self._project_root,
            project_assets=self._project_assets,
            project_shots=self._project_shots,
        )
        widget.setWindowFlags(widget.windowFlags() | Qt.Window)
        widget.resize(400, 500)
        widget.show()

        self.refresh()

    # Common
    def show_in_file_browser(self, path: str):
        url = QUrl.fromLocalFile(path)
        QDesktopServices.openUrl(url)

    def expand_all(self, tree_widget: QTreeWidget):
        tree_widget.expandAll()

    def collapse_all(self, tree_widget: QTreeWidget):
        tree_widget.collapseAll()


class FXCreateShotWidget(QWidget):
    def __init__(self, parent=None, project_name=None, project_root=None, project_assets=None, project_shots=None):
        super().__init__(parent)

        # Attributes
        self.project_name = project_name
        self._project_root = project_root
        self._project_assets = project_assets
        self._project_shots = project_shots

        # Methods
        self._create_ui()
        self._rename_ui()
        self._modify_ui()
        self._handle_connections()
        self._populate_sequences()

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
        self.group_box_metadata: QGroupBox = self.ui.group_box_metadata
        self.button_add_metadata: QPushButton = self.ui.button_add_metadata
        self.frame_metadata: QFrame = self.ui.frame_metadata
        self.button_box: QDialogButtonBox = self.ui.button_box

    def _handle_connections(self):
        """_summary_"""

        self.button_add_metadata.clicked.connect(self._add_metadata_line)

    def _modify_ui(self):
        """_summary_"""

        self.label_icon_sequence.setPixmap(fxicons.get_pixmap("camera_roll", 18))
        self.label_icon_shot.setPixmap(fxicons.get_pixmap("image", 18))
        self.label_icon_frame_range.setPixmap(fxicons.get_pixmap("alarm", 18))
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

    def _populate_sequences(self):
        """_summary_"""

        shots_dir = Path(self._project_root) / "production" / "shots"
        if not shots_dir.exists():
            return

        sequences = [sequence.name for sequence in shots_dir.iterdir() if sequence.is_dir()]
        self.combo_box_sequence.addItems(sequences)

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
        shot_dir = sequence_dir / shot
        shot = create_shot(shot, sequence_dir, self)
        if not shot:
            self.close()
            return

        # Get the metadata key-value pairs
        metadata = {}
        layout_metadata = self.frame_metadata.layout()

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

        # Close on completion
        self.close()


class FXCreateStepWidget(QWidget):
    def __init__(self, parent=None, project_name=None, project_root=None, project_assets=None, project_shots=None):
        super().__init__(parent)

        # Attributes
        self.project_name = project_name
        self._project_root = project_root
        self._project_assets = project_assets
        self._project_shots = project_shots

        # Methods
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
        self.setWindowTitle("Create Step")

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
                # Create shot
                # TODO: Create the step
                # button.clicked.connect(self._create_step)
            elif role == QDialogButtonBox.RejectRole:
                button.setIcon(fxicons.get_icon("close", color="#ec0811"))
                # Close
                button.clicked.connect(self.close)

    def _handle_connections(self):
        """_summary_"""

        self.list_steps.currentItemChanged.connect(self._populate_tasks)

    def _populate_steps(self):

        steps_file = Path(self._project_root) / ".pipeline" / "project_config" / "steps.yaml"
        if not steps_file.exists():
            return

        steps_data = yaml.safe_load(steps_file.read_text())

        for step in steps_data["steps"]:
            step_item = QListWidgetItem(step.get("name_long", None))
            step_item.setIcon(fxicons.get_icon(step.get("icon", "check_box_outline_blank")))
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


class FXCreateProjectWindow(fxwidgets.FXMainWindow):
    # TODO: Implement the create project window
    pass


def run_create_project():
    """Runs the create project window."""

    # TODO: Implement the runtime create project window
    pass


def get_project() -> Dict[str, Optional[str]]:
    """Gets the project path, name, assets path, and shots path from the
    environment file, or the environment variables (if set beforehand).

    Returns:
        Dict[str, Optional[str]]: A dictionary with keys
            'FXQUINOX_PROJECT_ROOT', 'FXQUINOX_PROJECT_NAME',
            'FXQUINOX_PROJECT_ASSETS', and 'FXQUINOX_PROJECT_SHOTS' pointing to
            their respective paths if found, `None` otherwise.
    """

    keys = ["FXQUINOX_PROJECT_ROOT", "FXQUINOX_PROJECT_NAME", "FXQUINOX_PROJECT_ASSETS", "FXQUINOX_PROJECT_SHOTS"]
    project_info = {key: None for key in keys}

    # Early return if the environment variables are set
    if all(os.getenv(key) for key in keys):
        _logger.info("Using environment variables")
        for key in keys:
            project_info[key] = os.getenv(key)
            _logger.debug(f"${key}: '{project_info[key]}'")
        return project_info

    # Else, parse the environment file
    try:
        with open(fxenvironment.FXQUINOX_ENV_FILE, "r") as file:
            for line in file:
                for key in keys:
                    if line.startswith(key):
                        _, value = line.strip().split("=", 1)
                        project_info[key] = value.strip("'\"")  # Remove quotes
                        break  # Move to the next line after finding a match

                # If all values are found, no need to continue reading the file
                if all(project_info.values()):
                    break

    except FileNotFoundError:
        _logger.error(f"File not found: '{fxenvironment.FXQUINOX_ENV_FILE.as_posix()}'")
        return project_info

    # Update environment variables
    for key, value in project_info.items():
        os.environ[key] = str(value)

    _logger.info("Using environment file")
    for key, value in project_info.items():
        _logger.debug(f"{key.replace('FXQUINOX_', '').replace('_', ' ').capitalize()}: '{value}'")

    return project_info


def set_project(
    launcher: Optional[FXLauncherSystemTray] = None, quit_on_last_window_closed: bool = False, project_path: str = None
) -> Optional[Tuple[str, str]]:
    """Sets the project path in the project browser.

    Args:
        launcher (FXLauncherSystemTray): The launcher instance to update the project name.
            Defaults to `None`.
        quit_on_last_window_closed (bool): Whether to quit the application when
            the last window is closed. Defaults to `False`.
        project_dir (str): The project directory to set. Defaults to `None`.

    Returns:
        Optional[Tuple[str, str]]: A tuple with project path and project name
            if set, `None` otherwise.
    """

    if not project_path:
        app = fxwidgets.FXApplication().instance()
        app.setQuitOnLastWindowClosed(quit_on_last_window_closed)

        project_path = QFileDialog.getExistingDirectory(
            caption="Select Project Directory",
            directory=QDir.homePath(),
            options=QFileDialog.ShowDirsOnly,
        )

    if project_path and check_project(project_path):
        project_path = Path(project_path).resolve().as_posix()

        # Save a file to hold the current project
        file_path = Path(fxenvironment.FXQUINOX_APPDATA) / "fxquinox.env"
        project_name = fxfiles.get_metadata(project_path, "name")

        # Read the existing content
        if file_path.exists():
            content = file_path.read_text()
        else:
            content = ""

        # Split the content into lines for easier manipulation
        lines = content.splitlines()

        # Track if lines were found and replaced
        root_replaced = False
        name_replaced = False
        assets_replaced = False
        shots_replaced = False

        # Replace or note the lines to append
        for i, line in enumerate(lines):
            if "FXQUINOX_PROJECT_ROOT=" in line:
                lines[i] = f"FXQUINOX_PROJECT_ROOT='{project_path}'"
                root_replaced = True
            elif "FXQUINOX_PROJECT_NAME=" in line:
                lines[i] = f"FXQUINOX_PROJECT_NAME='{project_name}'"
                name_replaced = True
            elif "FXQUINOX_PROJECT_ASSETS=" in line:
                lines[i] = f"FXQUINOX_PROJECT_ASSETS='{project_path}/production/assets'"
                assets_replaced = True
            elif "FXQUINOX_PROJECT_SHOTS=" in line:
                lines[i] = f"FXQUINOX_PROJECT_SHOTS='{project_path}/production/shots'"
                shots_replaced = True

        # Append lines if they were not found
        if not root_replaced:
            lines.append(f"FXQUINOX_PROJECT_ROOT='{project_path}'")
        if not name_replaced:
            lines.append(f"FXQUINOX_PROJECT_NAME='{project_name}'")
        if not assets_replaced:
            lines.append(f"FXQUINOX_PROJECT_ASSETS='{project_path}/production/assets'")
        if not shots_replaced:
            lines.append(f"FXQUINOX_PROJECT_SHOTS='{project_path}/production/shots'")

        # Join the lines back and write to the file
        content = "\n".join(lines)
        file_path.write_text(content)

        # Update the environment variables
        os.environ["FXQUINOX_PROJECT_ROOT"] = project_path
        os.environ["FXQUINOX_PROJECT_NAME"] = project_name
        os.environ["FXQUINOX_PROJECT_ASSETS"] = f"{project_path}/production/assets"
        os.environ["FXQUINOX_PROJECT_SHOTS"] = f"{project_path}/production/shots"

        # Emit signal to update the launcher label
        if launcher:
            launcher.project_changed.emit(project_path, project_name)

        _logger.info(f"Project path set to '{project_path}'")
        return project_path, project_name

    else:
        _logger.warning("Invalid project path")
        return None


def open_project_directory() -> None:
    """Opens the project directory in the system file manager."""

    project_info = get_project()
    project_root = project_info.get("FXQUINOX_PROJECT_ROOT", None)
    if project_root:
        open_directory(project_root)
    else:
        _logger.warning("No project set")


def open_directory(path: str) -> None:
    """Opens the given directory in the system file manager."""

    url = QUrl.fromLocalFile(path)
    QDesktopServices.openUrl(url)


def _is_process_running(pid: int) -> bool:
    """Check if there's a running process with the given PID.

    Args:
        pid (int): The process ID to check.

    Returns:
        bool: `True` if the process is running, `False` otherwise.
    """

    try:
        p = psutil.Process(pid)
        return p.is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False


def _check_and_create_lock(lock_file_path: str) -> bool:
    """Check for an existing lock and handle it appropriately.

    Args:
        lock_file_path (str): The path to the lock file.

    Returns:
        bool: `True` if the lock file was created, `False` otherwise (aka
            another instance is running).
    """

    lock_path = Path(lock_file_path)

    if lock_path.exists():
        pid = lock_path.read_text().strip()
        if pid and _is_process_running(int(pid)):
            # Another instance is running
            return False
        else:
            # The process is not running > overwrite the lock file
            lock_path.write_text(str(os.getpid()))
            return True
    else:
        lock_path.write_text(str(os.getpid()))
        return True


def _remove_lock(lock_file_path: str) -> None:
    """Remove the lock file.

    Args:
        lock_file_path (str): The path to the lock file.
    """

    lock_path = Path(lock_file_path)
    if lock_path.exists():
        lock_path.unlink()


def run_launcher(
    parent: QWidget = None, quit_on_last_window_closed: bool = True, show_splashscreen: bool = False
) -> None:
    """Runs the FX Launcher UI.

    Args:
        quit_on_last_window_closed (bool): Whether to quit the application when
            the last window is closed. Defaults to `True`.
        show_splashscreen (bool): Whether to show the splash screen.
            Defaults to `False`.
    """

    # Check for an existing lock file
    lock_file = Path(fxenvironment.FXQUINOX_TEMP) / "launcher.lock"
    if not _check_and_create_lock(lock_file):
        _logger.warning("Launcher already running")
        return
    else:
        _logger.debug(f"Lock file created: {lock_file.as_posix()}")

    # Get the current project
    project_info = get_project()
    project_root = project_info.get("FXQUINOX_PROJECT_ROOT", None)
    project_name = project_info.get("FXQUINOX_PROJECT_NAME", None)

    # If it doesn't exist but has been set in the environment file, error
    if project_root and not Path(project_root).exists():
        _logger.error(f"Project set in the environment file doesn't exist: '{project_root}'")
        # Ask the user if they want to delete the environment file, allowing
        # the creation of a new one from the launcher
        while True:
            confirmation = input(f"Delete the corrupted environment file? (y/n): ")
            if confirmation.lower() == "y":
                Path(fxenvironment.FXQUINOX_ENV_FILE).unlink()
                _logger.info(f"Environment '{Path(fxenvironment.FXQUINOX_ENV_FILE).as_posix()}' file deleted")
                break
            elif confirmation.lower() == "n":
                _logger.info(f"Deletion cancelled")
                return None
            else:
                _logger.warning("Please enter 'y' to continue or 'n' to cancel")

    # Application
    if not parent:
        app = fxwidgets.FXApplication().instance()
        app.setQuitOnLastWindowClosed(quit_on_last_window_closed)

    # Icon
    icon_path = (Path(__file__).parents[1] / "images" / "fxquinox_logo_light.svg").as_posix()

    if show_splashscreen:
        splash_image_path = (Path(__file__).parents[1] / "images" / "splash.png").as_posix()

        # Splashscreen
        information = textwrap.dedent(
            """\
        USD centric pipeline for feature animation and VFX projects. Made with love by Valentin Beaumont.

        This project is a very early work in progress and is not ready for production use.
        """
        )
        splashscreen = fxwidgets.FXSplashScreen(
            image_path=splash_image_path,
            icon=icon_path,
            title="Fxquinox",
            information=information,
            project=project_name or "No project set",
            version="0.0.1",
            company="fxquinox",
        )
        splashscreen.show()

        # ' Launcher
        splashscreen.showMessage("Communication with CG gods...")
        splashscreen.showMessage("Loading project...")
        temp_widget = _FXTempWidget(parent=None)
        splashscreen.showMessage("Starting launcher...")
        launcher = FXLauncherSystemTray(parent=None, icon=icon_path, project=project_name)
        splashscreen.finish(temp_widget)
    else:
        launcher = FXLauncherSystemTray(parent=None, icon=icon_path, project=project_name)

    launcher.show()
    _logger.info("Started launcher")

    if not parent:
        app.exec_()


def run_project_browser(parent: QWidget = None, quit_on_last_window_closed: bool = False) -> None:
    """Runs the project browser UI.

    Args:
        parent (QWidget): The parent widget. Defaults to `None`.
        quit_on_last_window_closed (bool): Whether to quit the application when
            the last window is closed. Defaults to `False`.
    """

    base_path = Path(__file__).resolve().parent
    images_path = base_path.parent / "images"

    if not parent:
        app = fxwidgets.FXApplication.instance()
        app.setQuitOnLastWindowClosed(quit_on_last_window_closed)

    # Get current project
    project_info = get_project()
    project_name = project_info.get("FXQUINOX_PROJECT_NAME", None)

    ui_file = base_path / "ui" / "project_browser.ui"
    icon_path = images_path / "fxquinox_logo_background_light.svg"

    window = FXProjectBrowserWindow(
        parent=parent if isinstance(parent, QWidget) else None,
        icon=icon_path.resolve().as_posix(),
        title="Project Browser",
        size=(1500, 900),
        project=project_name,
        version="0.0.1",
        company="fxquinox",
        ui_file=ui_file.resolve().as_posix(),
    )

    window.show()

    if not parent:
        app.exec_()


###### Runtime

# os.environ["FXQUINOX_DEBUG"] = "1"

if __name__ == "__main__":
    # Debug
    if os.getenv("FXQUINOX_DEBUG") == "1":
        _logger.info("Running in debug mode")
    # Production
    else:
        run_project_browser(parent=None, quit_on_last_window_closed=True)
        # run_launcher(parent=None, show_splashscreen=True)
