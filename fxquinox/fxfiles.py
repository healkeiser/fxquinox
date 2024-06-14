# Built-in
import os
import re
from typing import Dict, Any, Optional, Union

# Internal
from fxquinox import fxlog

# Log
_log = fxlog.get_logger(__name__)


###### CODE ####################################################################


def replace_backward_slashes(path: str) -> str:
    """Replaces backward slashes with forward slashes in a given path.

    Args:
        path (str): The input path containing backward slashes.

    Returns:
        str: The path with all backward slashes replaced by forward slashes.

    Examples:
        >>> replace_backward_slashes("C:\\Users\\User\\Documents")
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
        as_string (bool, optional): If `True`, returns the next version number as
            a string with the 'v' prefix. Defaults to `False`.

    Returns:
        Union[int, str]: The next version number to be used, incremented by one from the
            highest existing version. Returns 1 if no versioned files are found.

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
        """Generates a filename based on the attributes of the FX workfile template.

        Returns:
            str: The generated filename.
        """

        return f"{self.sequence}_{self.shot}_{self.step}_{self.task}_{self.version}"

    @classmethod
    def from_string(cls, input_string: str) -> "FXWorkfileTemplate":
        """Creates an FXWorkfileTemplate instance from a string.

        Args:
            input_string (str): The string containing information to create the instance.

        Returns:
            FXWorkfileTemplate: The FXWorkfileTemplate instance created from the input string.

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
            version = int(version.lstrip("v"))
            return cls(int(sequence), int(shot), step, task, version)
        else:
            raise ValueError("Invalid input string format")


if __name__ == "__main__":
    _template = FXWorkfileTemplate(sequence="000", shot="0010", step="LGT", task="main", version="v001")
    template_int = FXWorkfileTemplate.from_string(str(_template))
    template_str = str(template_int)
    _log.info(
        f"Test: {template_int.sequence} {template_int.shot} {template_int.step} {template_int.task} {template_int.version}"
    )
    _log.info(f"Test: {template_str}")
