# Built-in
import re


def is_valid_string(input_string: str) -> bool:
    """Check if a string is valid for use. Match only alphanumeric characters,
    underscores, or hyphens.

    Args:
        input_string (str): The string to check.

    Returns:
        bool: `True` if the string is valid, `False` otherwise.
    """

    pattern = r"^[a-zA-Z0-9_-]*$"
    return bool(re.match(pattern, input_string))


def transform_to_valid_string(input_string: str) -> str:
    """Transform a string into a valid format by keeping only alphanumeric
    characters, underscores, or hyphens.

    Args:
        input_string (str): The string to transform.

    Returns:
        str: The transformed string with only valid characters.
    """

    pattern = r"[^a-zA-Z0-9_-]"
    valid_string = re.sub(pattern, "", input_string)
    return valid_string
