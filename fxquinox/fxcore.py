"""The fxcore module provides a set of tools for managing and automating the creation of VFX entities."""

# Built-in
from functools import lru_cache
import json
import os
from pathlib import Path
import re
from typing import Union, Dict, Optional
import warnings

# Third-party
from fxgui import fxwidgets, fxicons
from qtpy.QtWidgets import QWidget
import yaml

# Internal
from fxquinox import fxlog, fxfiles

# Reload
from importlib import reload

reload(fxwidgets)
reload(fxicons)

# Log
_logger = fxlog.get_logger(__name__)
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


def _create_entity(entity_type: str, entity_name: str, base_dir: str = ".") -> None:
    """Generic function to create a new directory for a given entity type in
    the specified base directory.

    Args:
        entity_type (str): The type of entity to create.
        entity_name (str): The name of the entity to create.
        base_dir (str): The base directory in which to create the entity.
            Defaults to the current directory.
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
                return
            else:
                _logger.warning("Please enter 'y' to continue or 'N' to cancel")

    fxfiles.create_structure_from_dict(structure_dict, _base_dir_path)
    _logger.info(f"{entity_type.capitalize()} '{entity_name}' created in '{_base_dir_path}'")


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

    if not metadata_entity == entity_type and metadata_creator == "fxquinox":
        return False
    return True


###### Projects


class InvalidProjectError(Exception):
    """Exception raised when a project is not valid."""

    pass


def create_project(project_name: str, base_dir: str = ".") -> None:
    """Creates a new project directory structure.

    Args:
        project_name (str): The name of the project to create.
        base_dir (str): The base directory where the project will be created.
            Defaults to the current directory.
    """

    _create_entity(_PROJECT, project_name, base_dir)


###### Sequences


class InvalidSequenceError(Exception):
    """Exception raised when a sequence is not valid."""

    pass


class InvalidSequencesDirectoryError(Exception):
    """Exception raised when a sequences directory is not valid."""

    pass


def create_sequence(sequence_name: str, base_dir: str = ".") -> None:
    """Creates a new sequence directory structure within a project.

    Args:
        sequence_name (str): The name of the sequence to create.
        base_dir (str): The base directory where the sequence will be created,
            typically the "project/production/shots" directory.
            Defaults to the current directory.
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
    _create_entity(_SEQUENCE, sequence_name, base_dir_path)


def create_sequences(sequence_names: list[str], base_dir: str = ".") -> None:
    """Creates new sequence directory structures within a project.

    Args:
        sequence_names (list): The names of the sequences to create.
        base_dir (str): The base directory where the sequence will be created,
            typically the "project/production/shots" directory.
            Defaults to the current directory.
    """

    # Check the parent entity sequence "shots" directory validity before
    # creating the sequence
    base_dir_path = Path(base_dir).resolve()

    if not _check_shots_directory(base_dir_path):
        error_message = f"'{base_dir_path}' is not a valid shots directory"
        _logger.error(error_message)
        raise InvalidSequencesDirectoryError(error_message)

    # Create the sequences
    for sequence_name in sequence_names:
        _create_entity(_SEQUENCE, sequence_name, base_dir_path)


def check_sequence(base_dir: str = ".") -> Union[bool, Dict]:
    """Checks if a valid sequence directory structure exists within a project.

    Args:
        base_dir (str): The base directory where the sequence should be located,
            typically the "project/production/shots" directory.
            Defaults to the current directory.

    Returns:
        Union[bool, dict]: A tuple containing a boolean indicating if the sequence
            is valid and a dictionary with the sequence information.
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
    """

    return _check_entity(_SHOTS_DIR, base_dir)


###### Shots


class InvalidShotError(Exception):
    """Exception raised when a shot is not valid."""

    pass


def create_shot(shot_name: str, base_dir: str = ".") -> None:
    """Creates a new shot directory structure within a sequence.

    Args:
        shot_name (str): The name of the shot to create.
        base_dir (str): The base directory where the shot will be created,
            typically the "project/production/shots/sequence" directory.
            Defaults to the current directory.

    Examples:
        Python
        >>> create_shot("0010", "/path/to/sequence")

        CLI
        >>> fxcore.create_shot "0010" --base_dir "/path/to/sequence"
    """

    # Ensure right naming convention
    if len(shot_name) != 4:
        error_message = "Shot names should be exactly 4 characters long"
        _logger.error(error_message)
        raise ValueError(error_message)

    # Check the parent entity sequence validity before creating the shot
    base_dir_path = Path(base_dir).resolve()
    sequence_name = base_dir_path.name

    if not check_sequence(sequence_name, base_dir_path):
        error_message = f"'{sequence_name}' in '{base_dir_path.as_posix()}' is not a sequence"
        _logger.error(error_message)
        raise InvalidSequenceError(error_message)

    # Create the shot
    _create_entity(_SHOT, shot_name, base_dir_path)


def create_shots(shot_names: list[str], base_dir: str = ".") -> None:
    """Creates new shot directory structures within a sequence.

    Args:
        shot_names (list[str]): The names of the shots to create.
        base_dir (str): The base directory where the shots will be created,
            typically the "project/production/shots/sequence" directory.
            Defaults to the current directory.

    Examples:
        Python
        >>> create_shots(["0010", "0020"], "/path/to/sequence")

        CLI
        >>> fxcore.create_shots 0010,0020 --base_dir "/path/to/sequence"
    """

    # Check the parent entity sequence validity before creating the shot
    base_dir_path = Path(base_dir).resolve()
    sequence_name = base_dir_path.name

    if not check_sequence(sequence_name, base_dir_path):
        error_message = f"'{sequence_name}' in '{base_dir_path.as_posix()}' is not a sequence"
        _logger.error(error_message)
        raise InvalidSequenceError(error_message)

    # Proceed to create each shot if the sequence is valid
    for shot_name in shot_names:

        # Ensure right naming convention
        if len(shot_name) != 4:
            error_message = "Shot names should be exactly 4 characters long"
            _logger.error(error_message)
            raise ValueError(error_message)

        _create_entity(_SHOT, shot_name, base_dir_path)


def check_shot(base_dir: str = ".") -> Union[bool, Dict]:
    """Checks if a valid shot directory structure exists within a sequence.

    Args:
        base_dir (str): The base directory where the shot should be located,
            typically the "project/production/shots/sequence" directory.
            Defaults to the current directory.

    Returns:
        Union[bool, dict]: A tuple containing a boolean indicating if the shot
            is valid and a dictionary with the shot information.
    """

    return _check_entity(_SHOT, base_dir)


###### Assets


class InvalidAssetError(Exception):
    """Exception raised when an asset is not valid."""

    pass


class InvalidAssetsDirectoryError(Exception):
    """Exception raised when an assets directory is not valid."""

    pass


def create_asset(asset_name: str, base_dir: str = ".") -> None:
    """Creates a new asset directory structure within a project.

    Args:
        asset_name (str): The name of the asset to create.
        base_dir (str): The base directory where the asset will be created,
            typically the "project/production/assets" directory.
            Defaults to the current directory.
    """

    # Check the parent entity assets "assets" directory validity before
    # creating the asset
    base_dir_path = Path(base_dir).resolve()

    if not _check_assets_directory(base_dir_path):
        error_message = f"'{base_dir_path.as_posix()}' is not a valid assets directory"
        _logger.error(error_message)
        raise InvalidAssetsDirectoryError(error_message)

    # Create the asset
    _create_entity(_ASSET, asset_name, base_dir)


def create_assets(asset_names: list[str], base_dir: str = ".") -> None:
    """Creates new asset directory structures within a project.

    Args:
        asset_names (list): The names of the assets to create.
        base_dir (str): The base directory where the asset will be created,
            typically the "project/production/assets" directory.
            Defaults to the current directory.

    Examples:
        Python
        >>> create_assets(["character", "prop"], "/path/to/assets")

        CLI
        >>> fxcore.create_assets character,prop --base_dir "/path/to/assets"
    """

    # Check the parent entity sequence validity before creating the shot
    base_dir_path = Path(base_dir).resolve()

    if not _check_assets_directory(base_dir_path):
        error_message = f"'{base_dir_path.as_posix()}' is not a valid assets directory"
        _logger.error(error_message)
        raise InvalidAssetsDirectoryError(error_message)

    # Create the assets
    for asset_name in asset_names:
        _create_entity(_ASSET, asset_name, base_dir_path)


def check_asset(base_dir: str = ".") -> Union[bool, Dict]:
    """Checks if a valid asset directory structure exists within a project.

    Args:
        base_dir (str): The base directory where the asset should be located,
            typically the "project/production/assets" directory.
            Defaults to the current directory.

    Returns:
        Union[bool, Dict]: A tuple containing a boolean indicating if the asset
    """

    return _check_entity(_ASSET, base_dir)


def _check_assets_directory(base_dir: str = ".") -> Union[bool, Dict]:
    """Checks if a valid "assets" (which holds the assets) directory
    structure exists within a project.

    Args:
        base_dir (str): The base directory where the "assets" directory should
            be located, typically the "project/production" directory.
            Defaults to the current directory.

    Returns:
        Union[bool, Dict]: A tuple containing a boolean indicating if the assets
            directory is valid and a dictionary with the assets directory information.
    """

    return _check_entity(_ASSETS_DIR, base_dir)


###### UI


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
        self._rename_ui()
        self._create_icons()
        self._modify_ui()

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


def run_project_browser():
    """Runs the project browser UI."""

    ui_file = (Path(__file__).parent / "ui" / "project_browser.ui").as_posix()

    app = fxwidgets.FXApplication()
    window = FXProjectBrowser(
        parent=None,
        icon=None,
        title="FX Project Browser",
        size=(1500, 900),
        project="fxquinox",
        version="0.0.1",
        company="fxquinox",
        ui_file=ui_file,
    )
    window.show()
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

        # _fxcli.main(target_module=sys.modules[__name__], description=__doc__ if __doc__ else __name__)

        # UI
        run_project_browser()
