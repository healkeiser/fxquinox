"""The fxcore module provides a set of tools for managing and automating
the creation of VFX entities.
"""

# Built-in
from functools import lru_cache
import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

# Third-party
from fxgui import fxwidgets
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *
import yaml

# Internal
from fxquinox import fxenvironment, fxlog, fxfiles, fxutils, fxerrors, fxentities
from fxquinox.ui.fxwidgets import fxlauncher


# Log
_logger = fxlog.get_logger("fxcore")
_logger.setLevel(fxlog.DEBUG)


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

    structure_path = Path(fxenvironment._FXQUINOX_STRUCTURES) / f"{entity}_structure.{file_type}"
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
    _base_dir_path = base_dir_path.resolve().as_posix()
    entity_dir = base_dir_path / entity_name
    _logger.debug(f"Entity directory: '{entity_dir.resolve().as_posix()}'")

    structure_dict = _get_structure_dict(entity_type)
    structure_dict = fxfiles.replace_placeholders_in_dict(
        structure_dict,
        {
            # Common metadata
            entity_type.upper(): entity_name,  # Entity type
            f"{entity_type.upper()}_ROOT": _base_dir_path,  # Entity root directory
            "PATH": entity_dir.resolve().as_posix(),
            "PARENT": base_dir_path.name,
            # Project metadata
            "FPS": "24",
            # Sequence metadata
            # Shot metadata
            "CUT_IN": "None",
            "CUT_OUT": "None",
            # Asset metadata
            # Workfile metadata
        },
    )

    if Path(entity_dir).exists():
        if parent:
            confirmation = QMessageBox(parent)
            confirmation.setWindowTitle(f"Create {entity_type.capitalize()}")
            confirmation.setText(
                f"There's already a {entity_type} <b>{entity_name}</b> in <code>{_base_dir_path}</code>, do you want to continue?"
            )
            confirmation.setIcon(QMessageBox.Warning)
            confirmation.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirmation.setDefaultButton(QMessageBox.No)  # Set the default button to `No`
            confirmation.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Make the text selectable

            confirmation_response = confirmation.exec_()
            if confirmation_response == QMessageBox.No:
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


###### Project
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

    Info:
        Has a CLI counterpart.
    """

    return _create_entity(fxentities.entity.project, project_name, base_dir)


def check_project(base_dir: str = ".") -> bool:
    """Checks if a valid project directory structure exists.

    Args:
        base_dir (str): The base directory where the project should be located.
            Defaults to the current directory.

    Returns:
        bool: `True` if the project is valid, `False` otherwise.
    """

    return _check_entity(fxentities.entity.project, base_dir)


def get_project(from_file: bool = False) -> Dict[str, Optional[str]]:
    """Gets the project path, name, assets path, and shots path from the
    environment file, or the environment variables (if set beforehand).

    Args:
        from_file (bool): Whether to force read the environment file.
            Defaults to `False`.

    Returns:
        Dict[str, Optional[str]]: A dictionary with keys
            'FXQUINOX_PROJECT_ROOT', 'FXQUINOX_PROJECT_NAME',
            'FXQUINOX_PROJECT_ASSETS_PATH', and 'FXQUINOX_PROJECT_SHOTS_PATH'
            pointing to their respective paths if found, `None` otherwise.
    """

    def read_from_env() -> Dict[str, str]:
        """Reads the environment variables and returns the project information.

        Returns:
            Dict[str, str]: A dictionary with project information.
        """

        return {key: os.getenv(key) for key in keys}

    def ensure_configuration_exists():
        """Ensures the configuration file exists and creates it with default
        values if it doesn't.
        """

        config_path = Path(fxenvironment.FXQUINOX_APPDATA) / "fxquinox.cfg"
        default_config = {"project": {"root": "", "name": "", "assets_path": "", "shots_path": ""}}
        if not config_path.is_file():
            fxutils.update_configuration_file("fxquinox.cfg", default_config)

    def read_configuration() -> Dict[str, str]:
        """Reads the configuration file and returns the project information.

        Returns:
            Dict[str, str]: A dictionary with project information.
        """

        _config = fxutils.get_configuration_file_values(
            "fxquinox.cfg", {"project": ["root", "name", "assets_path", "shots_path"]}
        )
        return {
            "FXQUINOX_PROJECT_ROOT": _config["project"]["root"],
            "FXQUINOX_PROJECT_NAME": _config["project"]["name"],
            "FXQUINOX_PROJECT_ASSETS_PATH": _config["project"]["assets_path"],
            "FXQUINOX_PROJECT_SHOTS_PATH": _config["project"]["shots_path"],
        }

    def read_from_file() -> Dict[str, str]:
        """Reads the project information from the configuration file.

        Returns:
            Dict[str, str]: A dictionary with project information.
        """

        ensure_configuration_exists()
        return read_configuration()

    keys = [
        "FXQUINOX_PROJECT_ROOT",
        "FXQUINOX_PROJECT_NAME",
        "FXQUINOX_PROJECT_ASSETS_PATH",
        "FXQUINOX_PROJECT_SHOTS_PATH",
    ]
    project_info = {key: None for key in keys}

    if not from_file and all(os.getenv(key) for key in keys):
        _logger.debug("Accessing environment using environment variables")
        project_info.update(read_from_env())
    else:
        _logger.debug("Accessing environment using configuration file")
        project_info.update(read_from_file())

    # Update environment variables and log
    for key, value in project_info.items():
        os.environ[key] = str(value)
        _logger.debug(f"{key}: '{value}'")

    return project_info


def set_project(
    launcher: Optional[fxlauncher.FXLauncherSystemTray] = None,
    quit_on_last_window_closed: bool = False,
    project_path: str = None,
) -> Optional[Tuple[str, str]]:
    """Sets the project path in the project browser.

    Args:
        launcher (FXLauncherSystemTray): The launcher instance to update the
            project name. Defaults to `None`.
        quit_on_last_window_closed (bool): Whether to quit the application when
            the last window is closed. Defaults to `False`.
        project_dir (str): The project directory to set. Defaults to `None`.

    Returns:
        Optional[dict]: A dictionary with the project root, name, assets path,
            and shots path if set, `None` otherwise.
    """

    if not project_path:
        app = fxwidgets.FXApplication().instance()
        app.setQuitOnLastWindowClosed(quit_on_last_window_closed)

        project_path = QFileDialog.getExistingDirectory(
            caption="Select Project Directory",
            dir=QDir.homePath(),
            options=QFileDialog.ShowDirsOnly,
        )

    if project_path and check_project(project_path):
        project_path = Path(project_path).resolve().as_posix()

        # Save the current project to the config file
        project_name = fxfiles.get_metadata(project_path, "name")
        fxutils.update_configuration_file(
            "fxquinox.cfg",
            {
                "project": {
                    "root": project_path,
                    "name": project_name,
                    "assets_path": f"{project_path}/production/assets",
                    "shots_path": f"{project_path}/production/shots",
                }
            },
        )

        # Update the environment variables
        os.environ["FXQUINOX_PROJECT_ROOT"] = project_path
        os.environ["FXQUINOX_PROJECT_NAME"] = project_name
        os.environ["FXQUINOX_PROJECT_ASSETS_PATH"] = f"{project_path}/production/assets"
        os.environ["FXQUINOX_PROJECT_SHOTS_PATH"] = f"{project_path}/production/shots"

        project_info = get_project()

        # Emit signal to update the launcher label
        if launcher:
            _logger.debug(f"Launcher: {launcher}")
            _logger.debug("Emitting `project_changed` signal")
            launcher.project_changed.emit(project_info)

        _logger.info(f"Project path set to '{project_path}'")
        return project_info

    else:
        _logger.warning("Invalid project path")
        return None


###### Sequences
def create_sequence(sequence_name: str, base_dir: str = ".", parent: QWidget = None) -> Optional[str]:
    """Creates a new sequence directory structure within a project.

    Args:
        sequence_name (str): The name of the sequence to create.
        base_dir (str): The base directory where the sequence will be created,
            typically the "project/production/shots" directory.
            Defaults to the current directory.
        parent (QWidget): The parent widget for the message box. Only
            applicable in a GUI environment.

    Returns:
        Optional[str]: The name of the sequence if created, `None` otherwise.

    Examples:
        Python
        >>> create_sequence("010", "/path/to/shots")

        CLI
        >>> fxquinox.cli.fxcore.create_sequence 010 --base_dir "/path/to/shots"

    Info:
        Has a CLI counterpart.
    """

    # Check the parent entity sequence "shots" directory validity before
    # creating the sequence
    base_dir_path = Path(base_dir).resolve()

    if not check_shots_directory(base_dir_path):
        error_message = f"'{base_dir_path.as_posix()}' is not a valid shots directory"
        _logger.error(error_message)
        raise fxerrors.InvalidSequencesDirectoryError(error_message)

    # Create the sequence
    return _create_entity(fxentities.entity.sequence, sequence_name, base_dir_path, parent)


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

    Info:
        Has a CLI counterpart.
    """

    # Check the parent entity sequence "shots" directory validity before
    # creating the sequence
    base_dir_path = Path(base_dir).resolve()

    if not check_shots_directory(base_dir_path):
        error_message = f"'{base_dir_path}' is not a valid shots directory"
        _logger.error(error_message)
        raise fxerrors.InvalidSequencesDirectoryError(error_message)

    # Create the sequences
    sequences = []
    for sequence_name in sequence_names:
        _create_entity(fxentities.entity.sequence, sequence_name, base_dir_path)
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

    return _check_entity(fxentities.entity.sequence, base_dir)


# ? It could appear as this function should be in the shots section, but it's
# ? here because the `shots` directory is the one holding the sequences.
def check_shots_directory(base_dir: str = ".") -> bool:
    """Checks if a valid "shots" (which holds the sequences) directory
    structure exists within a project.

    Args:
        base_dir (str): The base directory where the "shots" directory should
            be located, typically the "project/production" directory.
            Defaults to the current directory.

    Returns:
        bool: `True` if the shots directory is valid, `False` otherwise.
    """

    return _check_entity(fxentities.entity.shots_dir, base_dir)


###### Shots
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

    Info:
        Has a CLI counterpart.
    """

    # Check the parent entity sequence validity before creating the shot
    base_dir_path = Path(base_dir).resolve()
    sequence_name = base_dir_path.name

    if not check_sequence(base_dir_path):
        error_message = f"'{sequence_name}' in '{base_dir_path.as_posix()}' is not a sequence"
        _logger.error(error_message)
        raise fxerrors.InvalidSequenceError(error_message)

    # Create the shot
    return _create_entity(fxentities.entity.shot, shot_name, base_dir_path, parent)


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

    Info:
        Has a CLI counterpart.
    """

    # Check the parent entity sequence validity before creating the shot
    base_dir_path = Path(base_dir).resolve()
    sequence_name = base_dir_path.name

    if not check_sequence(base_dir_path):
        error_message = f"'{sequence_name}' in '{base_dir_path.as_posix()}' is not a sequence"
        _logger.error(error_message)
        raise fxerrors.InvalidSequenceError(error_message)

    # Proceed to create each shot if the sequence is valid
    shots = []
    for shot_name in shot_names:
        # Ensure right naming convention
        if len(shot_name) != 4:
            error_message = "Shot names should be exactly 4 characters long"
            _logger.error(error_message)
            raise ValueError(error_message)

        _create_entity(fxentities.entity.shot, shot_name, base_dir_path)
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

    return _check_entity(fxentities.entity.shot, base_dir)


###### Assets
def create_asset(asset_name: str, base_dir: str = ".", parent: QWidget = None) -> Optional[str]:
    """Creates a new asset directory structure within a project.

    Args:
        asset_name (str): The name of the asset to create.
        base_dir (str): The base directory where the asset will be created,
            typically the "project/production/assets" directory.
            Defaults to the current directory.
        parent (QWidget): The parent widget for the message box. Only
            applicable in a GUI environment.

    Returns:
        Optional[str]: The name of the asset if created, `None` otherwise.

    Examples:
        Python
        >>> create_asset("charA", "/path/to/assets")

        CLI
        >>> fxquinox.cli.fxcore.create_asset charA --base_dir "/path/to/assets"

    Info:
        Has a CLI counterpart.
    """

    # Check the parent entity assets "assets" directory validity before
    # creating the asset
    base_dir_path = Path(base_dir).resolve()

    if not check_assets_directory(base_dir_path):
        error_message = f"'{base_dir_path.as_posix()}' is not a valid assets directory"
        _logger.error(error_message)
        raise fxerrors.InvalidAssetsDirectoryError(error_message)

    # Create the asset
    return _create_entity(fxentities.entity.asset, asset_name, base_dir, parent)


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

    Info:
        Has a CLI counterpart.
    """

    # Check the parent entity sequence validity before creating the shot
    base_dir_path = Path(base_dir).resolve()

    if not check_assets_directory(base_dir_path):
        error_message = f"'{base_dir_path.as_posix()}' is not a valid assets directory"
        _logger.error(error_message)
        raise fxerrors.InvalidAssetsDirectoryError(error_message)

    # Create the assets
    assets = []
    for asset_name in asset_names:
        _create_entity(fxentities.entity.asset, asset_name, base_dir_path)
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

    return _check_entity(fxentities.entity.asset, base_dir)


def check_assets_directory(base_dir: str = ".") -> bool:
    """Checks if a valid "assets" (which holds the assets) directory
    structure exists within a project.

    Args:
        base_dir (str): The base directory where the "assets" directory should
            be located, typically the "project/production" directory.
            Defaults to the current directory.

    Returns:
        bool: `True` if the assets directory is valid, `False` otherwise.
    """

    return _check_entity(fxentities.entity.assets_dir, base_dir)


###### Steps (departments)
def create_step(step_name: str, base_dir: str = ".", parent: QWidget = None) -> Optional[str]:
    """Creates a new step directory structure within a project.

    Args:
        step_name (str): The name of the step to create.
        base_dir (str): The base directory where the step will be created,
            typically the "project/production/steps" directory.
            Defaults to the current directory.
        parent (QWidget): The parent widget for the message box. Only
            applicable in a GUI environment.

    Returns:
        Optional[str]: The name of the step if created, `None` otherwise.

    Examples:
        Python
        >>> create_step("modeling", "/path/to/steps")

        CLI
        >>> fxquinox.cli.fxcore.create_step modeling --base_dir "/path/to/steps"

    Info:
        Has a CLI counterpart.
    """

    base_dir_path = Path(base_dir).resolve()

    if not check_workfiles_directory(base_dir_path):
        error_message = f"'{base_dir_path.as_posix()}' is not a valid workfiles directory"
        _logger.error(error_message)
        raise fxerrors.InvalidStepError(error_message)

    # Create the step
    return _create_entity(fxentities.entity.step, step_name, base_dir_path, parent)


def check_step(base_dir: str = ".") -> bool:
    """Checks if a valid step directory structure exists within a project.

    Args:
        base_dir (str): The base directory where the step should be located,
            typically the "project/production/steps" directory.
            Defaults to the current directory.

    Returns:
        bool: `True` if the step is valid, `False` otherwise.
    """

    return _check_entity(fxentities.entity.step, base_dir)


###### Tasks
def create_task(task_name: str, base_dir: str = ".", parent: QWidget = None) -> Optional[str]:
    """Creates a new task directory structure within a project.

    Args:
        task_name (str): The name of the task to create.
        base_dir (str): The base directory where the task will be created,
            typically the "project/production/tasks" directory.
            Defaults to the current directory.
        parent (QWidget): The parent widget for the message box. Only
            applicable in a GUI environment.

    Returns:
        Optional[str]: The name of the task if created, `None` otherwise.

    Examples:
        Python
        >>> create_task("rigging", "/path/to/tasks")

        CLI
        >>> fxquinox.cli.fxcore.create_task rigging --base_dir "/path/to/tasks"

    Info:
        Has a CLI counterpart.
    """

    base_dir_path = Path(base_dir).resolve()

    if not check_step(base_dir_path):
        error_message = f"'{base_dir_path.as_posix()}' is not a valid steps directory"
        _logger.error(error_message)
        raise fxerrors.InvalidTaskError(error_message)

    # Create the task
    return _create_entity(fxentities.entity.task, task_name, base_dir_path, parent)


def check_task(base_dir: str = ".") -> bool:
    """Checks if a valid task directory structure exists within a project.

    Args:
        base_dir (str): The base directory where the task should be located,
            typically the "project/production/tasks" directory.
            Defaults to the current directory.

    Returns:
        bool: `True` if the task is valid, `False` otherwise.
    """

    return _check_entity(fxentities.entity.task, base_dir)


###### Workfiles
def create_workfile(workfile_name: str, base_dir: str = ".", parent: QWidget = None) -> Optional[str]:
    """Creates a new workfile directory structure within a project.

    Args:
        workfile_name (str): The name of the workfile to create.
        base_dir (str): The base directory where the workfile will be created,
            typically the "project/production/workfiles" directory.
            Defaults to the current directory.
        parent (QWidget): The parent widget for the message box. Only
            applicable in a GUI environment.

    Returns:
        Optional[str]: The name of the workfile if created, `None` otherwise.

    Examples:
        Python
        >>> create_workfile("rigging_v001", "/path/to/workfiles")

        CLI
        >>> fxquinox.cli.fxcore.create_workfile rigging_v001 --base_dir "/path/to/workfiles"

    Info:
        Has a CLI counterpart.

    Bug:
        Not implemented yet.
    """

    base_dir_path = Path(base_dir).resolve()

    if not check_task(base_dir_path):
        error_message = f"'{base_dir_path.as_posix()}' is not a valid workfiles directory"
        _logger.error(error_message)
        raise fxerrors.InvalidTaskError(error_message)

    # Create the task
    return _create_entity(fxentities.entity.workfile, workfile_name, base_dir_path, parent)


def check_workfiles_directory(base_dir: str = ".") -> bool:
    """Checks if a valid workfile directory structure exists within a project.

    Args:
        base_dir (str): The base directory where the workfile should be located,
            typically the "project/production/workfiles" directory.
            Defaults to the current directory.

    Returns:
        bool: `True` if the workfile is valid, `False` otherwise.
    """

    return _check_entity(fxentities.entity.workfiles_dir, base_dir)
