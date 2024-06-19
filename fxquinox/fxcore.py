"""The fxcore module provides a set of tools for managing and automating the creation of VFX entitites."""

# Built-in
from functools import lru_cache
import json
import os
from pathlib import Path
import sys
from typing import Union, Dict
import warnings

# Third-party
import yaml

# Internal
from fxquinox import fxlog, fxfiles


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

# TODO: Revisit the whole check process with the 'entity' metadata


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

    if entity_dir.exists():
        confirmation = input(
            f"There's already a {entity_type} '{entity_name}' in '{_base_dir_path}', do you want to continue? (y/N): "
        )
        if confirmation.lower() != "y":
            _logger.info(f"{entity_type.capitalize()} creation cancelled")
            return

    try:
        fxfiles.create_structure_from_dict(structure_dict, _base_dir_path)
        _logger.info(f"{entity_type.capitalize()} '{entity_name}' created in '{_base_dir_path}'")
    except Exception as e:
        _logger.error(f"Failed to create {entity_type} '{entity_name}': {repr(e)}")


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
    metadata_entity = fxfiles.get_metadata(entity_path, "entity")
    _logger.debug(f"Directory: '{entity_path}'")
    _logger.debug(f"Metadata entity: '{metadata_entity}'")

    if not metadata_entity == entity_type:
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
        error_message = f"'{base_dir_path}' is not a valid shots directory"
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


def check_sequence(sequence_name: str, base_dir: str = ".") -> Union[bool, Dict]:
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

    return _check_entity(_SHOTS_DIR, Path(base_dir).resolve().as_posix())


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

    is_parent_sequence, sequence_info = check_sequence(sequence_name, base_dir_path)

    if not is_parent_sequence:
        error_message = f"'{sequence_name}' in '{base_dir_path}' is not a sequence"
        _logger.error(error_message)
        raise InvalidSequenceError(error_message)

    # Create the shot
    _create_entity(_SHOT, shot_name, base_dir_path)

    # Add the created shot to the `<sequence_name>_info` JSON file
    sequence_info["shots"].append(shot_name)
    sequence_info_path = base_dir_path / f".{sequence_info['sequence_name']}_info.json"
    json.dump(sequence_info, sequence_info_path.open("w"), indent=4)


def create_shots(shot_names: list[str], base_dir: str = ".") -> None:
    """Creates new shot directory structures within a sequence.

    This function checks the sequence validity once before creating all shots,
    optimizing the process for bulk shot creation.

    Args:
        shot_names (list[str]): The names of the shots to create.
        base_dir (str): The base directory where the shots will be created,
            typically the "project/production/shots/sequence" directory.
            Defaults to the current directory.

    Examples:
        Python
        >>> create_shots(["0010", "0020"], "/path/to/sequence")

        CLI
        >>> fxcore.create_shots "0010" "0020" --base_dir "/path/to/sequence"
    """

    # Check the sequence validity once before creating all shots
    _parent_directory = Path(base_dir).parent.absolute()
    parent_directory = _parent_directory.resolve().as_posix()
    parent_name = _parent_directory.name

    is_parent_sequence, _ = check_sequence(parent_name, parent_directory)

    if not is_parent_sequence:
        error_message = f"'{parent_name}' in '{parent_directory}' is not a sequence"
        _logger.error(error_message)
        raise InvalidSequenceError(error_message)

    # Proceed to create each shot if the sequence is valid
    for shot_name in shot_names:

        # Ensure right naming convention
        if len(shot_name) != 4:
            error_message = "Shot names should be exactly 4 characters long"
            _logger.error(error_message)
            raise ValueError(error_message)

        _create_entity(_SHOT, shot_name, parent_directory)


def check_shot(shot_name: str, base_dir: str = ".") -> Union[bool, Dict]:
    """Checks if a valid shot directory structure exists within a sequence.

    Args:
        shot_name (str): The name of the shot to check.
        base_dir (str): The base directory where the shot should be located,
            typically the "project/production/shots/sequence" directory.
            Defaults to the current directory.

    Returns:
        Union[bool, dict]: A tuple containing a boolean indicating if the shot
            is valid and a dictionary with the shot information.
    """

    return _check_entity(_SHOT, shot_name, base_dir)


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

    # Check the parent entity assets directory validity before creating the asset
    base_dir_path = Path(base_dir).resolve()
    is_parent_assets_directory, assets_directory_info = check_assets_directory(base_dir_path)

    if not is_parent_assets_directory:
        error_message = f"'{base_dir_path}' is not a valid assets directory"
        _logger.error(error_message)
        raise InvalidAssetsDirectoryError(error_message)

    # Create the asset
    _create_entity(_ASSET, asset_name, base_dir)

    # Add the created asset to the `assets_info` JSON file
    assets_directory_info["assets"].append(asset_name)
    assets_directory_info_path = base_dir_path / f".{assets_directory_info['entity_type']}_info.json"
    json.dump(assets_directory_info, assets_directory_info_path.open("w"), indent=4)


def create_assets(asset_names: list[str], base_dir: str = ".") -> None:
    """Creates new asset directory structures within a project.

    Args:
        asset_names (list): The names of the assets to create.
        base_dir (str): The base directory where the asset will be created,
            typically the "project/production/assets" directory.
            Defaults to the current directory.
    """

    for asset_name in asset_names:
        create_asset(asset_name, base_dir)


def check_asset(asset_name: str, base_dir: str = ".") -> Union[bool, Dict]:
    """Checks if a valid asset directory structure exists within a project.

    Args:
        asset_name (str): The name of the asset to check.
        base_dir (str): The base directory where the asset should be located,
            typically the "project/production/assets" directory.
            Defaults to the current directory.

    Returns:
        Union[bool, Dict]: A tuple containing a boolean indicating if the asset
    """

    return _check_entity(_ASSET, asset_name, base_dir)


def check_assets_directory(base_dir: str = ".") -> Union[bool, Dict]:
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

    return _check_entity(_ASSETS_DIR, _ASSETS_DIR, base_dir)


###### Runtime


if __name__ == "__main__":
    # Debug
    if os.getenv("FXQUINOX_DEBUG") == "1":
        _logger.info("Running in debug mode")
    else:
        from fxquinox import _fxcli

        _fxcli.main(target_module=sys.modules[__name__], description=__doc__ if __doc__ else __name__)
