"""The fxcore module provides a set of tools for managing and automating
the creation of VFX entities.
"""

# Built-in
from functools import lru_cache
import json
import os
from pathlib import Path
import textwrap
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
from fxquinox.tools import fxprojectbrowser, fxlauncher


# Log
_logger = fxlog.get_logger("fxquinox.fxcore")
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


###### Projects
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
    """

    # Check the parent entity sequence "shots" directory validity before
    # creating the sequence
    base_dir_path = Path(base_dir).resolve()

    if not _check_shots_directory(base_dir_path):
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
    """

    # Check the parent entity sequence "shots" directory validity before
    # creating the sequence
    base_dir_path = Path(base_dir).resolve()

    if not _check_shots_directory(base_dir_path):
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
    """

    # Check the parent entity assets "assets" directory validity before
    # creating the asset
    base_dir_path = Path(base_dir).resolve()

    if not _check_assets_directory(base_dir_path):
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
    """

    # Check the parent entity sequence validity before creating the shot
    base_dir_path = Path(base_dir).resolve()

    if not _check_assets_directory(base_dir_path):
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
    """

    base_dir_path = Path(base_dir).resolve()

    if not _check_workfiles_directory(base_dir_path):
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
    """

    base_dir_path = Path(base_dir).resolve()

    if not check_task(base_dir_path):
        error_message = f"'{base_dir_path.as_posix()}' is not a valid workfiles directory"
        _logger.error(error_message)
        raise fxerrors.InvalidTaskError(error_message)

    # Create the task
    return _create_entity(fxentities.entity.workfile, workfile_name, base_dir_path, parent)


def _check_workfiles_directory(base_dir: str = ".") -> bool:
    """Checks if a valid workfile directory structure exists within a project.

    Args:
        base_dir (str): The base directory where the workfile should be located,
            typically the "project/production/workfiles" directory.
            Defaults to the current directory.

    Returns:
        bool: `True` if the workfile is valid, `False` otherwise.
    """

    return _check_entity(fxentities.entity.workfiles_dir, base_dir)


###### UI
def run_create_project():
    """Runs the create project UI."""

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
        _logger.info("Accessing environment using environment variables")
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

    _logger.info("Accessing environment using environment file")
    for key, value in project_info.items():
        _logger.debug(f"{key.replace('FXQUINOX_', '').replace('_', ' ').capitalize()}: '{value}'")

    return project_info


def set_project(
    launcher: Optional[fxlauncher.FXLauncherSystemTray] = None,
    quit_on_last_window_closed: bool = False,
    project_path: str = None,
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

        config_file_name = "general.cfg"
        config_section_name = "set_project"
        config_option_name = "last_project_directory"

        previous_directory = (
            fxutils.get_configuration_file_value(config_file_name, config_section_name, config_option_name)
            or Path.home().resolve().as_posix()
        )

        project_path = QFileDialog.getExistingDirectory(
            caption="Select Project Directory",
            directory=previous_directory,
            options=QFileDialog.ShowDirsOnly,
        )

    if project_path and check_project(project_path):
        project_path = Path(project_path).resolve().as_posix()

        # Update the configuration file with last traveled directory
        fxutils.update_configuration_file(config_file_name, config_section_name, config_option_name, project_path)

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
        fxutils.open_directory(project_root)
    else:
        _logger.warning("No project set")


def run_launcher(
    parent: QWidget = None, quit_on_last_window_closed: bool = True, show_splashscreen: bool = False
) -> None:
    """Runs the launcher UI.

    Args:
        quit_on_last_window_closed (bool): Whether to quit the application when
            the last window is closed. Defaults to `True`.
        show_splashscreen (bool): Whether to show the splash screen.
            Defaults to `False`.
    """

    # Check for an existing lock file
    lock_file = Path(fxenvironment.FXQUINOX_TEMP) / "launcher.lock"
    if not fxutils.check_and_create_lock(lock_file):
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
        temp_widget = fxlauncher._FXTempWidget(parent=None)
        splashscreen.showMessage("Starting launcher...")
        launcher = fxlauncher.FXLauncherSystemTray(parent=None, icon=icon_path, project=project_name)
        splashscreen.finish(temp_widget)
    else:
        launcher = fxlauncher.FXLauncherSystemTray(parent=None, icon=icon_path, project=project_name)

    launcher.show()
    _logger.info("Started launcher")

    if not parent:
        app.exec_()


def run_project_browser(
    parent: QWidget = None, quit_on_last_window_closed: bool = False, dcc: fxentities.DCC = fxentities.DCC.standalone
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

    window = fxprojectbrowser.FXProjectBrowserWindow(
        parent=parent if isinstance(parent, QWidget) else None,
        icon=icon_path.resolve().as_posix(),
        title="Project Browser",
        size=(2000, 1200),
        project=project_name,
        version="0.0.1",
        company="fxquinox",
        ui_file=ui_file.resolve().as_posix(),
        dcc=dcc,
    )
    window.show()
    # window.setStyleSheet(fxstyle.load_stylesheet())

    if not parent:
        app.exec_()

    return window


###### Runtime

# os.environ["FXQUINOX_DEBUG"] = "1"

if __name__ == "__main__":
    # Debug
    if os.getenv("FXQUINOX_DEBUG") == "1":
        _logger.info("Running in debug mode")
    # Production
    else:
        run_project_browser(parent=None, quit_on_last_window_closed=True, dcc=fxentities.DCC.houdini)
        # run_launcher(parent=None, show_splashscreen=True)
