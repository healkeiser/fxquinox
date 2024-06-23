"""The fxcore module provides a set of tools for managing and automating the creation of VFX entities."""

# Built-in
from ast import Tuple
from functools import lru_cache
import json
import os
from pathlib import Path
import sys
import textwrap
from typing import Dict, Optional, Tuple
import warnings

# Third-party
from fxgui import fxwidgets, fxicons, fxstyle, fxutils as fxguiutils
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *
import yaml

# Internal
from fxquinox import fxenvironment, fxlog, fxfiles


# Log
_logger = fxlog.get_logger("fxquinox.fxcore")
_logger.setLevel(fxlog.DEBUG)

# Warnings
# XXX: Need to check why the hell this is happening
warnings.filterwarnings("ignore", message=".*found in sys.modules after import of package.*", category=RuntimeWarning)

# Globals
_PROJECT = "project"
_SEQUENCE = "sequence"
_SHOTS_DIR = "shots"
_SHOT = "shot"
_ASSETS_DIR = "assets"
_ASSET = "asset"


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


def _create_entity(entity_type: str, entity_name: str, base_dir: str = ".") -> Optional[str]:
    """Generic function to create a new directory for a given entity type in
    the specified base directory.

    Args:
        entity_type (str): The type of entity to create.
        entity_name (str): The name of the entity to create.
        base_dir (str): The base directory in which to create the entity.
            Defaults to the current directory.

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
        while True:
            confirmation = input(
                f"There's already a {entity_type} '{entity_name}' in "
                f"'{_base_dir_path}', do you want to continue? (y/N): "
            )
            if confirmation.lower() == "y":
                break
            elif confirmation.lower() == "n":
                _logger.info(f"{entity_type.capitalize()} creation cancelled")
                return None
            else:
                _logger.warning("Please enter 'y' to continue or 'N' to cancel")

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


def create_shot(shot_name: str, base_dir: str = ".") -> Optional[str]:
    """Creates a new shot directory structure within a sequence.

    Args:
        shot_name (str): The name of the shot to create.
        base_dir (str): The base directory where the shot will be created,
            typically the "project/production/shots/sequence" directory.
            Defaults to the current directory.

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
    return _create_entity(_SHOT, shot_name, base_dir_path)


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

    if not check_sequence(sequence_name, base_dir_path):
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


###### UI


class FXLauncher(fxwidgets.FXSystemTray):
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
        self.colors = fxstyle.load_colors_from_jsonc()

        # Methods
        self.__create_actions()
        self._create_label()
        self._create_app_launcher()
        self.__handle_connections()
        self._update_label(project_name=self.project)
        self._toggle_action_state(project_name=self.project)

    def __handle_connections(self) -> None:
        """Connects the signals to the slots."""

        self.project_changed.connect(self._update_label)
        self.project_changed.connect(self._toggle_action_state)

    def __create_actions(self) -> None:
        """Creates the actions for the system tray."""

        self.set_project_action = fxguiutils.create_action(
            self.tray_menu,
            "Set Project",
            fxicons.get_icon("switch_right"),
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
        self.label = QLabel(self.project if self.project else "No project set")
        layout.addWidget(self.label)
        layout.setContentsMargins(10, 10, 10, 10)
        label_action = QWidgetAction(self.tray_menu)
        label_action.setDefaultWidget(container_widget)
        self.tray_menu.insertAction(self.set_project_action, label_action)
        self._set_label_style()

    def _create_app_launcher(self) -> None:
        """Creates the application launcher as a grid."""

        container_widget = QWidget()
        container_widget.setObjectName("app_launcher_container")
        container_widget.setStyleSheet(
            "#app_launcher_container { background-color: #131212; border-top: 1px solid #424242; border-bottom: 1px solid #424242}"
        )
        grid_layout = QGridLayout(container_widget)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_layout.setSpacing(10)
        apps = sorted(["Maya", "Houdini", "Nuke", "Blender", "Substance Painter", "Photoshop"])
        icons_path = Path(__file__).parents[1] / "images" / "icons" / "apps"

        row, col = 0, 0
        button_size = QSize(96, 96)
        for app in apps:
            icon_file = icons_path / f"{app.lower().replace(' ', '_')}.svg"
            button = QPushButton()
            button.setIcon(QIcon(str(icon_file)))
            button.setIconSize(QSize(64, 64))
            button.setFixedSize(button_size)
            fxguiutils.set_formatted_tooltip(button, "Application", app)
            grid_layout.addWidget(button, row, col)
            col += 1
            if col >= 3:
                row += 1
                col = 0

        # grid_layout.setContentsMargins(0, 0, 0, 0)
        self.list_apps_action = QWidgetAction(self.tray_menu)
        self.list_apps_action.setDefaultWidget(container_widget)
        self.tray_menu.insertAction(self.open_project_browser_action, self.list_apps_action)

    def _update_label(self, project_path: str = None, project_name: str = None) -> None:
        """Updates the label text with the current project name."""

        self.label.setText(project_name)
        self._set_label_style(project_path, project_name)

    def _set_label_style(self, project_path: str = None, project_name: str = None) -> None:
        """Sets the label stylesheet based on the current project status."""

        if project_name:
            color = self.colors["feedback"]["success"]["light"]
        else:
            color = self.colors["feedback"]["warning"]["light"]
        self.label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12pt;")

    def _toggle_action_state(self, project_path: str = None, project_name: str = None) -> None:
        """Toggles the state of the actions based on the project status."""

        if project_name:
            self.open_project_browser_action.setEnabled(True)
            self.open_project_directory_action.setEnabled(True)
            self.list_apps_action.setEnabled(True)
        else:
            self.open_project_browser_action.setEnabled(False)
            self.open_project_directory_action.setEnabled(False)
            self.list_apps_action.setEnabled(False)


class _FXTempWidget(QWidget):
    """A temporary widget that will be linked to display the splashscreen, as
    we can't `splashcreen.finish()` without a QWidget."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGeometry(0, 0, 0, 0)
        self.hide()
        self.close()


class FXProjectBrowser(fxwidgets.FXMainWindow):
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
        #
        project_root: Optional[str] = None,
        project_name: Optional[str] = None,
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

        # Attributes
        self._project_root = project_root
        self._project_name = project_name

        # Methods
        self._rename_ui()
        self._create_icons()
        self._modify_ui()
        self._populate_assets()
        self._populate_shots()

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

    def _create_icons(self):
        """_summary_"""

        self.icon_search = fxicons.get_pixmap("search", 18)

    def _modify_ui(self):
        """Modifies the UI elements."""

        # Icons
        self.label_icon_filter_assets.setPixmap(self.icon_search)
        self.label_icon_filter_shots.setPixmap(self.icon_search)

    def _populate_shots(self) -> None:

        if not self._project_root:
            return

        shots_dir = Path(self._project_root) / "production" / "shots"
        if not shots_dir.exists():
            return

        for sequence in shots_dir.iterdir():
            if not sequence.is_dir():
                continue

            sequence_item = QTreeWidgetItem(self.tree_widget_shots)
            sequence_item.setText(0, sequence.name)

            for shot in sequence.iterdir():
                if not shot.is_dir():
                    continue

                shot_item = QTreeWidgetItem(sequence_item)
                shot_item.setText(0, shot.name)

    def _populate_assets(self) -> None:

        if not self._project_root:
            return

        assets_dir = Path(self._project_root) / "production" / "assets"
        if not assets_dir.exists():
            return

        for asset in assets_dir.iterdir():
            if not asset.is_dir():
                continue

            asset_item = QTreeWidgetItem(self.tree_widget_assets)
            asset_item.setText(0, asset.name)


def get_project() -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Gets the project path and name from the environment file.

    Returns:
        Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]: The
            project path, name, assets path and shots path if found,
            `None` otherwise.
    """

    # Early return if the environment variables are set
    if (
        os.getenv("FXQUINOX_PROJECT_ROOT")
        and os.getenv("FXQUINOX_PROJECT_NAME")
        and os.getenv("FXQUINOX_PROJECT_ASSETS")
        and os.getenv("FXQUINOX_PROJECT_SHOTS")
    ):
        _logger.debug(f"Environment variables set")
        _logger.debug(f"$FQUINOX_PROJECT_ROOT: '{os.getenv('FXQUINOX_PROJECT_ROOT')}'")
        _logger.debug(f"$FXQUINOX_PROJECT_NAME: '{os.getenv('FXQUINOX_PROJECT_NAME')}'")
        _logger.debug(f"$FXQUINOX_PROJECT_ASSETS: '{os.getenv('FXQUINOX_PROJECT_ASSETS')}'")
        _logger.debug(f"$FXQUINOX_PROJECT_SHOTS: '{os.getenv('FXQUINOX_PROJECT_SHOTS')}'")

        return (
            os.getenv("FXQUINOX_PROJECT_ROOT"),
            os.getenv("FXQUINOX_PROJECT_NAME"),
            os.getenv("FXQUINOX_PROJECT_ASSETS"),
            os.getenv("FXQUINOX_PROJECT_SHOTS"),
        )

    project_root_key = "FXQUINOX_PROJECT_ROOT"
    project_name_key = "FXQUINOX_PROJECT_NAME"
    project_assets_key = "FXQUINOX_PROJECT_ASSETS"
    project_shots_key = "FXQUINOX_PROJECT_SHOTS"

    project_root = None
    project_name = None
    project_assets = None
    project_shots = None

    try:
        with open(fxenvironment.FXQUINOX_ENV_FILE, "r") as file:
            for line in file:
                if line.startswith(project_root_key):
                    _, project_root = line.strip().split("=", 1)
                    project_root = project_root.strip("'\"")  # Remove quotes
                elif line.startswith(project_name_key):
                    _, project_name = line.strip().split("=", 1)
                    project_name = project_name.strip("'\"")  # Remove quotes
                elif line.startswith(project_assets_key):
                    _, project_assets = line.strip().split("=", 1)
                    project_assets = project_assets.strip("'\"")
                elif line.startswith(project_shots_key):
                    _, project_shots = line.strip().split("=", 1)
                    project_shots = project_shots.strip("'\"")

                # If values are found, no need to continue reading the file
                if (
                    project_root is not None
                    and project_name is not None
                    and project_assets is not None
                    and project_shots is not None
                ):
                    break

    except FileNotFoundError:
        _logger.error(f"File not found: '{fxenvironment.FXQUINOX_ENV_FILE.as_posix()}'")

    os.environ["FXQUINOX_PROJECT_ROOT"] = str(project_root)
    os.environ["FXQUINOX_PROJECT_NAME"] = str(project_root)
    os.environ["FXQUINOX_PROJECT_ASSETS"] = str(project_assets)
    os.environ["FXQUINOX_PROJECT_SHOTS"] = str(project_shots)

    return project_root, project_name, project_assets, project_shots


def set_project(launcher=Optional[FXLauncher], quit_on_last_window_closed: bool = False) -> Optional[Tuple[str, str]]:
    """Sets the project path in the project browser.

    Args:
        quit_on_last_window_closed (bool): Whether to quit the application when
            the last window is closed. Defaults to `False`.

    Returns:
        Optional[Tuple[str, str]]: A tuple with project path and project name
            if set, `None` otherwise.
    """

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

        # Emit signal to update the launcher label
        if launcher:
            launcher.project_changed.emit(project_path, project_name)

        # Update the environment variables
        os.environ["FXQUINOX_PROJECT_ROOT"] = project_path
        os.environ["FXQUINOX_PROJECT_NAME"] = project_name
        os.environ["FXQUINOX_PROJECT_ASSETS"] = f"{project_path}/production/assets"
        os.environ["FXQUINOX_PROJECT_SHOTS"] = f"{project_path}/production/shots"
        _logger.info(f"Project path set to '{project_path}'")
        return project_path, project_name

    else:
        _logger.warning("Invalid project path")
        return None


def open_project_directory() -> None:
    """Opens the project directory in the system file manager."""

    project_root, _, _, _ = get_project()
    if project_root:
        open_directory(project_root)
    else:
        _logger.warning("No project set")


def open_directory(path: str) -> None:
    """Opens the given directory in the system file manager."""

    url = QUrl.fromLocalFile(path)
    QDesktopServices.openUrl(url)


def run_launcher(quit_on_last_window_closed: bool = True, show_splashscreen: bool = False) -> None:
    """Runs the FX Launcher UI.

    Args:
        quit_on_last_window_closed (bool): Whether to quit the application when
            the last window is closed. Defaults to `True`.
        show_splashscreen (bool): Whether to show the splash screen.
            Defaults to `False`.
    """

    # Allow only one instance of the launcher
    lock_file_path = Path(fxenvironment.FXQUINOX_TEMP) / "launcher.lock"
    if lock_file_path.exists():
        _logger.warning("Launcher already running")
        return
    lock_file_path.touch()

    # Application
    app = fxwidgets.FXApplication().instance()
    app.setQuitOnLastWindowClosed(quit_on_last_window_closed)

    # Get the current project
    project_root, project_name, _, _ = get_project()

    # Icon
    icon_path = (Path(__file__).parents[1] / "images" / "fxquinox_logo_light.svg").as_posix()

    if show_splashscreen:
        splash_image_path = (Path(__file__).parents[1] / "images" / "splash.png").as_posix()

        # Splashscreen
        information = textwrap.dedent(
            """\
        USD centric pipeline for feature animation and VFX projects. Made with love by Valentin Beaumont.
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
        launcher = FXLauncher(parent=None, icon=icon_path, project=project_name)
        splashscreen.finish(temp_widget)
    else:
        launcher = FXLauncher(parent=None, icon=icon_path, project=project_name)

    launcher.show()
    _logger.info("Started launcher")
    app.exec_()

    # Remove lock file (allowing to run the launcher again)
    lock_file_path.unlink()


def run_project_browser(quit_on_last_window_closed: bool = False) -> None:
    """Runs the project browser UI.

    Args:
        quit_on_last_window_closed (bool): Whether to quit the application when
            the last window is closed. Defaults to `False`.
    """

    app = fxwidgets.FXApplication.instance()
    app.setQuitOnLastWindowClosed(quit_on_last_window_closed)

    # Get current project
    project_root, project_name, _, _ = get_project()

    print(">>> ", project_name)

    ui_file = (Path(__file__).parent / "ui" / "project_browser.ui").as_posix()
    window = FXProjectBrowser(
        parent=None,
        icon=None,
        title="FX Project Browser",
        size=(1500, 900),
        project=project_name,
        version="0.0.1",
        company="fxquinox",
        ui_file=ui_file,
        #
        project_root=project_root,
        project_name=project_name,
    )
    window.show()
    window.setAttribute(Qt.WA_DeleteOnClose)
    _logger.info("Started project browser")
    app.exec_()


###### Runtime

# os.environ["FXQUINOX_DEBUG"] = "1"

if __name__ == "__main__":
    # Debug
    if os.getenv("FXQUINOX_DEBUG") == "1":
        _logger.info("Running in debug mode")
    else:
        # CLI
        # from fxquinox import _fxcli

        # excludes = ["get_project", "set_project", "open_project_directory", "run_launcher", "run_project_browser"]
        # _fxcli.main(
        #     target_module=sys.modules[__name__],
        #     description=__doc__ if __doc__ else __name__,
        #     exclude_functions=excludes,
        # )

        # UI
        # sequences = create_sequences(["010", "020", "030"], "D:/Projects/test_project/production/shots")
        # for sequence in sequences:
        #     create_shot("0010", f"D:/Projects/test_project/production/shots/{sequence}")
        run_launcher()
