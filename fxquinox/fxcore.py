"""The fxcore module provides a set of tools for managing and automating the creation of VFX entitites."""

# Built-in
import json
from functools import lru_cache
from pathlib import Path
import sys
import warnings

# Internal
from fxquinox import fxlog, fxfiles


# Log
_logger = fxlog.get_logger(__name__)
_logger.setLevel(fxlog.DEBUG)

# Warnings
# XXX: Need to check why the hell this is happening
warnings.filterwarnings("ignore", message=".*found in sys.modules after import of package.*", category=RuntimeWarning)


@lru_cache(maxsize=None)
def _get_structure_dict(entity: str) -> dict:
    """Reads the project structure from the JSON file and returns it.

    Args:
        entity (str): The entity type for which the structure is needed.

    Returns:
        dict: The project structure dictionary.

    Note:
        This function is decorated with `lru_cache` to avoid reading the file every time.
    """

    structure_path = Path(__file__).parent / "structures" / f"{entity}_structure.json"
    if structure_path.exists():
        return json.loads(structure_path.read_text())
    else:
        _logger.error(f"Structure file '{structure_path}' not found")
        return {}


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

    structure_dict = fxfiles.replace_in_json(
        structure_dict,
        {
            f"<{entity_type}>": entity_name,
            "<project_root>": entity_dir.resolve().as_posix() if entity_type == "project" else "",
        },
    )

    if entity_dir.exists():
        confirmation = input(
            f"There's already a {entity_type} '{entity_name}' in '{base_dir}', do you want to continue? (y/N): "
        )
        if confirmation.lower() != "y":
            _logger.info(f"{entity_type.capitalize()} creation cancelled")
            return

    try:
        fxfiles.create_structure_from_dict(structure_dict, str(base_dir_path))
        _logger.info(f"{entity_type.capitalize()} '{entity_name}' created in '{str(base_dir_path)}'")
    except Exception as e:
        _logger.error(f"Failed to create {entity_type} '{entity_name}': {str(e)}")


def create_project(project_name: str, base_dir: str = ".") -> None:
    """Creates a new project directory structure.

    Args:
        project_name (str): The name of the project to create.
        base_dir (str): The base directory where the project will be created.
            Defaults to the current directory.
    """

    _create_entity("project", project_name, base_dir)


def create_sequence(sequence_name: str, base_dir: str = ".") -> None:
    """Creates a new sequence directory structure within a project.

    Args:
        sequence_name (str): The name of the sequence to create.
        base_dir (str): The base directory where the sequence will be created,
            typically the "project/production/shots" directory.
            Defaults to the current directory.
    """

    if len(sequence_name) != 3:
        _logger.error("Sequence names should be exactly 4 characters long")
        return

    if not base_dir.endswith("production/shots"):
        _logger.error(
            "Sequence should be created under the '$FXQUINOX_PROJECT_ROOT/production/shots' directory",
        )
        return

    _create_entity("sequence", sequence_name, base_dir)


def create_shot(shot_name: str, base_dir: str = ".") -> None:
    """Creates a new shot directory structure within a sequence.

    Args:
        shot_name (str): The name of the shot to create.
        base_dir (str): The base directory where the shot will be created,
            typically the "project/production/shots/sequence" directory.
            Defaults to the current directory.
    """

    if len(shot_name) != 4:
        _logger.error("Shot names should be exactly 4 characters long")
        return

    _create_entity("shot", shot_name, base_dir)


def create_shots(shot_names: list[str], base_dir: str = ".") -> None:
    """Creates a new shot directory structure within a sequence.

    Args:
        shot_names (list): The names of the shots to create.
        base_dir (str): The base directory where the shot will be created,
            typically the "project/production/shots/sequence" directory.
            Defaults to the current directory.
    """

    for shot_name in shot_names:
        create_shot(shot_name, base_dir)


def create_asset(asset_name: str, base_dir: str = ".") -> None:
    """Creates a new asset directory structure within a project.

    Args:
        asset_name (str): The name of the asset to create.
        base_dir (str): The base directory where the asset will be created,
            typically the "project/production/assets" directory.
            Defaults to the current directory.
    """

    _create_entity("asset", asset_name, base_dir)


if __name__ == "__main__":
    from fxquinox import _fxcli

    _fxcli.main(target_module=sys.modules[__name__], description=__doc__ if __doc__ else __name__)
