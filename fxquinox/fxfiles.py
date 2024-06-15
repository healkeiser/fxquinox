# Built-in
import os
import json
from pathlib import Path
import re
from typing import Dict, Any, Optional, Union

# Internal
from fxquinox import fxlog


# Log
_log = fxlog.get_logger(__name__)

# Globals
_EXTENSIONS = {
    "maya": ["ma", "mb"],
    "houdini": ["hip", "hipnc", "hiplc"],
    "nuke": ["nk"],
    "blender": ["blend"],
    "substance": ["sbsar", "sbs"],
    "photoshop": ["psd"],
}


def path_to_unix(path: str) -> str:
    """Replaces backward slashes with forward slashes (Unix format) in a given
    path.

    Args:
        path (str): The input path containing backward slashes.

    Returns:
        str: The path with all backward slashes replaced by forward slashes.

    Examples:
        >>> path_to_unix("C:\\Users\\User\\Documents")
        "C:/Users/User/Documents"
    """

    return path.replace("\\", "/")


def create_structure_from_dict(directory_structure: Dict[str, Any], parent_path: str = ".") -> None:
    """Recursively creates folders and files based on the provided directory
    structure.

    Args:
        directory_structure (dict): The directory structure in JSON format.
        parent_path (str, optional): The parent path where the directory
            structure should be created. Defaults to current directory (`"."`).

    Examples:
        >>> with open("directory_structure_with_files.json", "r") as file:
        >>>     directory_structure = json.load(file)
        >>> create_folders_and_files(directory_structure)

    """

    for name, content in directory_structure.items():
        path = os.path.join(parent_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure_from_dict(content, path)
        else:
            with open(path, "w") as file:
                file.write(content)


def replace_in_json(data: Dict, replacements: Dict) -> Dict:
    """Replaces placeholders in a JSON object with values from a dictionary.

    Args:
        data (Dict): The JSON data as a dictionary.
        replacements (Dict): A dictionary mapping placeholder strings to replacement values.

    Returns:
        Dict: A new dictionary with the replacements made.
    """

    if isinstance(data, str):
        # Handle string values (e.g., within quotes)
        for placeholder, replacement in replacements.items():
            data = data.replace(placeholder, replacement)
        return data
    elif isinstance(data, dict):
        # Recursively replace in dictionaries
        return {replace_in_json(k, replacements): replace_in_json(v, replacements) for k, v in data.items()}
    elif isinstance(data, list):
        # Recursively replace in lists
        return [replace_in_json(item, replacements) for item in data]
    else:
        # Return other data types unchanged
        return data


def get_next_version(path: str, as_string: bool = False) -> Union[int, str]:
    """Determines the next version number based on the existing versioned files
    in the given directory.

    This function scans the specified directory for files with version numbers
    at the end of their names, in the format `_vNNN` where `N` is a digit.
    It identifies the highest version number currently present and returns the
    next version number, incremented by one.

    Args:
        path (str): The path to the directory containing the versioned files.
        as_string (bool, optional): If `True`, returns the next version number
        as a string with the 'v' prefix. Defaults to `False`.

    Returns:
        Union[int, str]: The next version number to be used, incremented by one
            from the highest existing version. Returns 1 if no versioned files
            are found.

    Examples:
        >>> get_next_version("/path/to/your/directory")
        4
        >>> get_next_version("/path/to/your/directory", as_string=True)
        "v004"
    """

    # Compile the regex pattern
    version_pattern = re.compile(r"_v(\d{3})$")

    # Initialize maximum version to 0
    max_version = 0

    # Scan given directory
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                match = version_pattern.search(entry.name)
                if match:
                    version_num = int(match.group(1))
                    if version_num > max_version:
                        max_version = version_num

    # Return the next version number
    next_version = max_version + 1
    return f"v{next_version:03d}" if as_string else next_version


def extract_version_integer_value(string: str) -> Optional[int]:
    """Extracts the integer value from a string in the format `"vXXX"`.

    Parameters:
        string (str): The input string containing the value in the format `"vXXX"`.

    Returns:
        int: The integer value extracted from the input string.

    Examples:
        >>> extract_version_integer_value("v001")
        1
        >>> extract_version_integer_value("abc123")
        None
    """

    return int(string[1:]) if string.startswith("v") else None


class FXProjectTemplate:
    """A class representing an FX project template.

    Attributes:
        name (str): The name of the project.
        root (str): The root directory of the project.
        info (dict): The project information.
    """

    def __init__(self, name: str, root: str, info: dict):
        self.name = name
        self.root = root
        self.info = info

    def __str__(self) -> str:
        """Returns a string representation of the FX project template.

        Returns:
            str: The string representation of the FX project template.
        """

        return f"{self.name} ({self.root})"

    @classmethod
    def from_json(cls, json_data: dict) -> "FXProjectTemplate":
        """Creates an FXProjectTemplate instance from a JSON object.

        Args:
            json_data (dict): The JSON data containing the project template
                information.

        Returns:
            FXProjectTemplate: The FXProjectTemplate instance created from the
                JSON data.

        Examples:
            >>> project_info = json.loads(
            >>>     Path.joinpath(
            >>>         Path("C:/path/to/project"), f"projectname_info.json"
            >>>     ).read_text()
            >>> )
            >>> project = FXProjectTemplate.from_json(project_info)
        """

        return cls(json_data["name"], json_data["root"], json_data["info"])

    @classmethod
    def from_string(cls, input_string: str) -> "FXProjectTemplate":
        """Creates an FXProjectTemplate instance from a string.

        Args:
            input_string (str): The string containing information to create the
            instance.

        Returns:
            FXProjectTemplate: The FXProjectTemplate instance created from
                the input string.

        Examples:
            >>> project = FXProjectTemplate.from_string("C:/path/to/project")
            >>> print(project.name, project.root)
            "Project Name", "C:/path/to/project"
        """

        name = Path(input_string).name
        root = Path(input_string).resolve().as_posix()
        structure = json.loads(Path.joinpath(Path(input_string), f"{name}_info.json").read_text())
        return cls(name, root, structure)


class FXWorkfileTemplate:
    """A class representing an FX workfile template.

    Attributes:
        sequence (str): The sequence number.
        shot (str): The shot number.
        step (str): The step in the FX workflow.
        task (str): The task associated with the workfile.
        version (str): The version number.
    """

    def __init__(self, sequence: str, shot: str, step: str, task: str, version: str):
        self.sequence = sequence
        self.shot = shot
        self.step = step
        self.task = task
        self.version = version

    def __str__(self) -> str:
        """Returns a string representation of the FX workfile template.

        Returns:
            str: The string representation of the FX workfile template.
        """

        return self.generate_filename()

    def generate_filename(self) -> str:
        """Generates a filename based on the attributes of the FX workfile
        template.

        Returns:
            str: The generated filename.
        """

        return f"{self.sequence}_{self.shot}_{self.step}_{self.task}_{self.version}"

    @classmethod
    def from_string(cls, input_string: str, return_int: bool = True) -> "FXWorkfileTemplate":
        """Creates an FXWorkfileTemplate instance from a string.

        Args:
            input_string (str): The string containing information to create the
            instance.
            return_int (bool, optional): If `True`, returns the sequence, shot
                and version as integers.

        Returns:
            FXWorkfileTemplate: The FXWorkfileTemplate instance created from
                the input string.

        Raises:
            ValueError: If the input string format is invalid.

        Examples:
            >>> workfile = FXWorkfileTemplate.from_string("000_0020_LGT_main_v001")
            >>> print(workfile.sequence, workfile.shot)
            "000", "0020"
        """

        parts = input_string.split("_")

        if len(parts) == 5:
            sequence, shot, step, task, version = parts
            if return_int:
                return cls(int(sequence), int(shot), step, task, int(version.lstrip("v")))
            return cls(sequence, shot, step, task, version)
        else:
            raise ValueError("Invalid input string format")


if __name__ == "__main__":
    _workfile = FXWorkfileTemplate(sequence="000", shot="0010", step="LGT", task="main", version="v001")
    _workfile = FXWorkfileTemplate.from_string(str(_workfile), False)
    _log.info(
        f"{type(_workfile).__name__}:\n    {str(_workfile)}, {_workfile.sequence}, {_workfile.shot}, {_workfile.step}",
    )

    _project = FXProjectTemplate.from_string("D:/Projects/_test_000")
    _log.info(
        f"{type(_project).__name__}:\n    {str(_project)}, {_project.name}, {_project.root}, {_project.info}",
    )
