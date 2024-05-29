import os


def create_project(project_name: str, base_dir: str = ".") -> None:
    """Creates a new project directory with the specified name.

    This function creates a new directory with the given project name in the
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

    # Define the project structure
    project_structure = {
        "src": "source code",
        "data": "data files",
        "docs": "documentation",
    }

    # Create the project directory
    project_dir = os.path.join(base_dir, project_name)
    os.makedirs(project_dir, exist_ok=True)

    # Create subdirectories
    for subdir, subdir_desc in project_structure.items():
        subdir_path = os.path.join(project_dir, subdir)
        os.makedirs(subdir_path, exist_ok=True)
        print(f"Created '{subdir}' directory for {subdir_desc}.")

    print(f"Project '{project_name}' created in '{base_dir}'.")
