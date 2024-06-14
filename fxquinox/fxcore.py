"""The fxcore module provides a set of tools for managing and automating the creation of projects, sequences, shots,
and assets within a digital production environment.
It leverages a JSON-based project structure definition to ensure consistency across different projects.
The module includes functionalities to create new projects with a predefined directory structure, as well as to
add sequences, shots, and assets to existing projects. It is designed to be easily integrated into larger pipeline
tools or used standalone for small to medium-sized projects.
"""

# Built-in
import json
from functools import lru_cache
from pathlib import Path
import sys

# Internal
from fxquinox import fxlog, fxfiles, _fxcli

# Log
_logger = fxlog.get_logger(__name__)


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


def create_project(project_name: str, base_dir: str = ".") -> None:
    """Creates a new directory with the given project name in the
    specified base directory. It also creates subdirectories for storing the
    project's source code, data, and documentation.

    Args:
        project_name (str): The name of the new project directory.
        base_dir (str, optional): The base directory where the project directory
            will be created. Defaults to the current working directory.

    Returns:
        None

    Examples:
        >>> create_project("my_project")
        Project 'my_project' created in current directory.
        >>> create_project("my_project", "/path/to/your/directory")
        Project 'my_project' created in '/path/to/your/directory'.
    """

    # Get the project directory to create
    base_dir_path = Path(base_dir)
    project_dir = base_dir_path / project_name

    # Get the project structure dictionary
    structure_dict = _get_structure_dict("project")

    # Replace the placeholders in the structure dictionary
    structure_dict = fxfiles.replace_in_json(
        structure_dict,
        {
            "<project>": project_name,
            "<project_path>": fxfiles.replace_backward_slashes(str(project_dir)),
        },
    )

    # If the project directory already exists, ask for confirmation
    if project_dir.exists():
        confirmation = input(
            f"There's already a project '{project_name}' in '{base_dir}', do you want to continue? (y/N): "
        )
        if confirmation.lower() != "y":
            _logger.info("Project creation cancelled")
            return

    # Create the project directory and its structure
    try:
        fxfiles.create_structure_from_dict(structure_dict, str(base_dir_path))
        _logger.info(f"Project '{project_name}' created in '{str(base_dir_path)}'")
    except Exception as e:
        _logger.error(f"Failed to create project '{project_name}': {str(e)}")


def create_sequence(sequence_name: str, base_dir: str = ".") -> None:
    """_summary_

    Args:
        sequence_name (str): _description_
        base_dir (str, optional): _description_. Defaults to ".".
    """


def create_shot(shot_name: str, base_dir: str = ".") -> None:
    """_summary_

    Args:
        shot_name (str): _description_
        base_dir (str, optional): _description_. Defaults to (`"."`).
    """


def create_asset(asset_name: str, base_dir: str = ".") -> None:
    """_summary_

    Args:
        asset_name (str): _description_
        base_dir (str, optional): _description_. Defaults to (`"."`).
    """


if __name__ == "__main__":
    _fxcli.main(
        target_module=sys.modules[__name__],
        description=__doc__ if __doc__ else __name__,
    )
