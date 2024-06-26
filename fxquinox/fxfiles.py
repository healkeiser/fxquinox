# Built-in
import os
import json
from pathlib import Path
import platform
import re
from typing import Dict, Any, Optional, Union, List, Tuple

# Internal
from fxquinox import fxlog


# Log
_logger = fxlog.get_logger("fxquinox.fxfiles")
_logger.setLevel(fxlog.DEBUG)

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


###### ! Old


def _create_structure_from_dict(
    directory_structure: Dict[str, Any], parent_path: str = ".", folders: List[str] = None, files: List[str] = None
) -> Tuple[List[str], List[str]]:
    """Recursively creates folders and files based on the provided directory
    structure and returns lists of created folders and files.

    Args:
        directory_structure (dict): The directory structure in JSON format.
        parent_path (str, optional): The parent path where the directory
            structure should be created. Defaults to current directory (`"."`).
        folders (List[str], optional): List of created folders. Used for recursion.
        files (List[str], optional): List of created files. Used for recursion.

    Returns:
        Tuple[List[str], List[str]]: A tuple containing two lists - the first
            with folders and the second with files created.

    Examples:
        >>> with open("directory_structure_with_files.json", "r") as file:
        >>>     directory_structure = json.load(file)
        >>> folders, files = _create_structure_from_dict(directory_structure)
        >>> print(f"Created folders: {folders}")
        >>> print(f"Created files: {files}")

    """

    if folders is None:
        folders = []
    if files is None:
        files = []

    for name, content in directory_structure.items():
        path = os.path.join(parent_path, name)
        if isinstance(content, dict):
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                folders.append(path)
            _create_structure_from_dict(content, path, folders, files)
        else:
            with open(path, "w") as file:
                file.write(content)
            files.append(path)

    return folders, files


def _replace_placeholders_in_dict(data: Dict, replacements: Dict) -> Dict:
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
        return {
            _replace_placeholders_in_dict(k, replacements): _replace_placeholders_in_dict(v, replacements)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        # Recursively replace in lists
        return [_replace_placeholders_in_dict(item, replacements) for item in data]
    else:
        # Return other data types unchanged
        return data


###### ' New


def create_structure_from_dict(structure_dict: dict, base_dir: str = ".") -> None:
    """Creates the directory structure based on the provided dict structure.

    Args:
        structure_dict (dict): The dictionary containing the structure.
        base_dir (str): The base directory where the structure will be created.
    """

    for root_name, root_item in structure_dict.items():
        root_path = Path(base_dir) / root_name
        if root_item["type"] == "folder":
            root_path.mkdir(parents=True, exist_ok=True)
            _logger.debug(f"Created folder: '{Path(root_path).as_posix()}'")
            set_multiple_metadata(str(root_path), root_item.get("metadata", {}))
            if "children" in root_item:
                for child in root_item["children"]:
                    create_child_from_dict(child, str(root_path))


def create_child_from_dict(child_dict: dict, parent_dir: str) -> None:
    """Recursively creates child folders and files based on the provided dict
    structure.

    Args:
        child_dict (dict): The dictionary containing the child structure.
        parent_dir (str): The parent directory where the child will be created.
    """

    child_path = Path(parent_dir) / child_dict["name"]

    # Folder
    if child_dict["type"] == "folder":
        child_path.mkdir(parents=True, exist_ok=True)
        _logger.debug(f"Created folder: '{Path(child_path).as_posix()}'")
        set_multiple_metadata(str(child_path), child_dict.get("metadata", {}))
        if "children" in child_dict:
            for child in child_dict["children"]:
                create_child_from_dict(child, str(child_path))

    # File
    elif child_dict["type"] == "file":
        child_path.write_text(child_dict.get("content", ""))
        _logger.debug(f"Created file: '{Path(child_path).as_posix()}'")
        set_multiple_metadata(str(child_path), child_dict.get("metadata", {}))


def replace_placeholders_in_dict(data: Dict, replacements: Dict) -> Dict:
    """Recursively replaces placeholders in a dictionary with values from another dictionary.

    Args:
        data (Dict): The dictionary to process.
        replacements (Dict): The dictionary containing placeholder-replacement pairs.

    Returns:
        Dict: The dictionary with placeholders replaced by values.
    """

    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            new_key = replace_placeholders_in_string(k, replacements)
            new_value = replace_placeholders_in_dict(v, replacements)
            new_dict[new_key] = new_value
        return new_dict
    elif isinstance(data, list):
        return [replace_placeholders_in_dict(item, replacements) for item in data]
    elif isinstance(data, str):
        return replace_placeholders_in_string(data, replacements)
    else:
        return data


def replace_placeholders_in_string(s: str, replacements: Dict) -> str:
    """Replaces placeholders in a string with values from a dictionary.

    Note:
        Placeholders are in the format `$placeholder$`.

    Args:
        s (str): The string to process.
        replacements (Dict): The dictionary containing placeholder-replacement pairs.

    Returns:
        str: The string with placeholders replaced by values.
    """

    for key, value in replacements.items():
        s = s.replace(f"${key}$", value)
    return s


###### Metadata


def set_metadata(file_path: str, metadata_name: str, metadata_value: str) -> Optional[str]:
    # Convert non-string values to JSON strings
    if not isinstance(metadata_value, str):
        metadata_value = json.dumps(metadata_value)

    if platform.system() == "Windows":
        # Windows: Use NTFS streams for metadata
        stream_name = file_path + ":" + metadata_name
        with open(stream_name, "w") as stream:
            stream.write(metadata_value)
    else:
        # Unix-like: Use extended attributes
        # Ensure metadata_name is prefixed with 'user.'
        if not metadata_name.startswith("user."):
            metadata_name = "user." + metadata_name
        os.setxattr(file_path, metadata_name.encode(), metadata_value.encode())


def set_multiple_metadata(file_path: str, metadata: Dict[str, str]) -> None:
    """Set multiple metadata entries for a file.

    Args:
        file_path (str): Path to the file.
        metadata (Dict[str, str]): Dictionary of metadata names and values to set.
    """

    for metadata_name, metadata_value in metadata.items():
        # Convert non-string values to JSON strings
        if not isinstance(metadata_value, str):
            metadata_value = json.dumps(metadata_value)

        if platform.system() == "Windows":
            # Windows: Use NTFS streams for metadata
            stream_name = file_path + ":" + metadata_name
            with open(stream_name, "w") as stream:
                stream.write(metadata_value)
        else:
            # Unix-like: Use extended attributes
            # Ensure metadata_name is prefixed with 'user.'
            if not metadata_name.startswith("user."):
                metadata_name = "user." + metadata_name
            os.setxattr(file_path, metadata_name.encode(), metadata_value.encode())


def get_metadata(file_path: str, metadata_name: str) -> Optional[str]:
    if platform.system() == "Windows":
        # Windows: Retrieve metadata from NTFS stream
        stream_name = file_path + ":" + metadata_name
        try:
            with open(stream_name, "r") as stream:
                return stream.read()
        except FileNotFoundError:
            return None  # Stream not found
    else:
        # Unix-like: Retrieve extended attribute
        # Ensure metadata_name is prefixed with 'user.'
        if not metadata_name.startswith("user."):
            metadata_name = "user." + metadata_name
        try:
            return os.getxattr(file_path, metadata_name.encode()).decode()
        except FileNotFoundError:
            return None  # Attribute not found


def get_multiple_metadata(file_path: str, metadata_names: List[str]) -> Dict[str, Optional[str]]:
    """Retrieve multiple metadata entries for a file.

    Args:
        file_path (str): Path to the file.
        metadata_names (List[str]): List of metadata names to retrieve.

    Returns:
        Dictionary of metadata names and their values. If a metadata entry is
        not found, its value is `None`.
    """
    metadatas = {}
    for metadata_name in metadata_names:
        if platform.system() == "Windows":
            # Windows: Retrieve metadata from NTFS stream
            stream_name = file_path + ":" + metadata_name
            try:
                with open(stream_name, "r") as stream:
                    metadatas[metadata_name] = stream.read()
            except FileNotFoundError:
                metadatas[metadata_name] = None  # Stream not found
        else:
            # Unix-like: Retrieve extended attribute
            # Ensure metadata_name is prefixed with 'user.'
            if not metadata_name.startswith("user."):
                metadata_name = "user." + metadata_name
            try:
                metadatas[metadata_name] = os.getxattr(file_path, metadata_name.encode()).decode()
            except FileNotFoundError:
                metadatas[metadata_name] = None  # Attribute not found
    return metadatas


def delete_metadata(file_path: str, metadata_name) -> None:
    if platform.system() == "Windows":
        # Windows: Delete NTFS stream by opening and closing it in write mode
        stream_name = file_path + ":" + metadata_name
        open(stream_name, "w").close()
    else:
        # Unix-like: Remove extended attribute
        if not metadata_name.startswith("user."):
            metadata_name = "user." + metadata_name
        os.removexattr(file_path, metadata_name.encode())


def clear_metadata(file_path: str) -> None:
    if platform.system() == "Windows":
        # Windows: Clearing all metadata is complex due to lack of direct support
        # This function will not handle clearing all metadata on Windows
        pass
    else:
        # Unix-like: List and remove all extended attributes
        attrs = os.listxattr(file_path)
        for attr in attrs:
            os.removexattr(file_path, attr)


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
                return cls(int(sequence), int(shot), step, task, extract_version_integer_value(version))
            return cls(sequence, shot, step, task, version)
        else:
            raise ValueError("Invalid input string format")


if __name__ == "__main__":
    # Workfile template
    _workfile = FXWorkfileTemplate(sequence="000", shot="0010", step="LGT", task="main", version="v001")
    _workfile = FXWorkfileTemplate.from_string(str(_workfile), False)
    _logger.info(
        f"{type(_workfile).__name__} (str): {str(_workfile)}, {_workfile.sequence}, {_workfile.shot}, {_workfile.step}, {_workfile.version}",
    )
    _workfile = FXWorkfileTemplate.from_string(str(_workfile), True)
    _logger.info(
        f"{type(_workfile).__name__} (int): {str(_workfile)}, {_workfile.sequence}, {_workfile.shot}, {_workfile.step}, {_workfile.version}",
    )

    # Project template
    _project = FXProjectTemplate.from_string("D:/Projects/_test_000")
    _logger.info(
        f"{type(_project).__name__}: {str(_project)}, {_project.name}, {_project.root}, {_project.info}",
    )
