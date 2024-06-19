"""Allows to automatically generate CLI tools from Python modules.

Examples:
    Set up the CLI in an external Python module
    >>> if __name__ == "__main__":
    >>>     from fxquinox import _fxcli
    >>>     _fxcli.main(
    ...         target_module=sys.modules[__name__], description=__doc__ if __doc__ else __name__
    ...     )

    Run the CLI tool in the terminal
    >>> python -m fxquinox.fxcore -h
    usage: fxcore.py [-h] {create_asset,create_project,create_sequence,create_shot} ...
"""

# Built-in
import argparse
import inspect
import re
from types import ModuleType

# Third-party
from colorama import just_fix_windows_console, Fore, Style

# Internal
from fxquinox import fxenvironment


# Initialize colorama
just_fix_windows_console()


def _parse_docstring(docstring: str) -> dict:
    """Parses a docstring into its components: description, arguments, and
    return type, supporting multiline descriptions.

    Args:
        docstring (str): The docstring to parse.

    Returns:
        dict: A dictionary with 'description', 'args', and 'returns' keys,
            where 'description' is a string containing the first paragraph of
            the docstring, 'args' is a list of dictionaries each containing
            'name', 'type', and 'description' for each argument, and 'returns'
            is a dictionary with 'type' and 'description' for the return value.

    Note:
        The docstring should follow the Google style guide for docstrings.

    Warning:
        Each docstring block should be separeted by an empty line.

    Examples:
        >>> docstring = '''
        ...    This is a docstring.
        ...
        ...    Args:
        ...        arg_1 (str): Argument 1 description.
        ...        arg_2 (str): Argument 2 description.
        ...
        ...    Returns:
        ...        str: Return value description.
        ...    '''
        >>> parsed = _parse_docstring(docstring)
        >>> print(parsed)
        {
            "description": "This is a docstring.",
            "args": {
                "arg_1": {"type": "str", "description": "Argument 1 description."},
                "arg_2": {"type": "str", "description": "Argument 2 description."}
            },
            "returns": {"type": "str", "description": "Return value description."}
        }
    """

    # Initialize a dictionary to hold the parsed components of the docstring
    parsed = {"description": "", "args": {}, "returns": {}, "examples": []}

    # Split the docstring into lines and strip leading/trailing whitespace
    lines = [line.strip() for line in docstring.split("\n")]

    # Track the current section being parsed (description, args, or returns)
    current_section = "description"

    # Keep track of the current argument being processed
    current_arg = None

    for line in lines:
        # Check for the start of the 'Args' section
        if line.startswith("Args:"):
            current_section = "args"
            continue

        # Check for the start of the 'Returns' section
        elif line.startswith("Returns:"):
            current_section = "returns"
            continue

        # Check for the start of the 'Examples' section
        elif line.startswith("Examples:"):
            current_section = "examples"
            continue

        # ! `Description` section
        if current_section == "description":
            # Append the line to the description, with a space if it's not the first line
            parsed["description"] += " " + line if parsed["description"] else line

        # ! `Arguments` section
        elif current_section == "args":
            # Match the argument pattern: name (type): description
            arg_match = re.match(r"^(\w+) \((\w+)\): (.+)$", line)
            if arg_match:
                # Extract argument name, type, and description from the match
                current_arg = arg_match.group(1)
                arg_type = arg_match.group(2)
                arg_desc = arg_match.group(3)
                # Store the extracted information in the parsed dictionary
                parsed["args"][current_arg] = {"type": arg_type, "description": arg_desc}
            elif current_arg:
                # If the line is part of a multiline argument description, append it
                parsed["args"][current_arg]["description"] += " " + line

        # ! `Returns` section
        elif current_section == "returns":
            # If the return type hasn't been parsed yet, parse it
            if "type" not in parsed["returns"]:  # First line after "Returns:" is the return info
                returns_match = re.match(r"^(\w+): (.+)$", line)
                if returns_match:
                    # Extract return type and description from the match
                    return_type = returns_match.group(1)
                    return_desc = returns_match.group(2)

                    # Store the extracted information in the parsed dictionary
                    parsed["returns"] = {"type": return_type, "description": return_desc}
            else:
                # If the line is part of a multiline return description, append it
                parsed["returns"]["description"] += " " + line

        # ! `Examples` section
        elif current_section == "examples":
            # Append the line directly to the examples list, preserving formatting
            if line:  # Optionally, skip empty lines
                parsed["examples"].append(line)

    return parsed


def _auto_generate_parser(
    target_module: ModuleType, description: str, exclude_functions: list[str] = []
) -> argparse.ArgumentParser:
    """Automatically generates an argparse parser based on the functions
    defined in the given module. It uses function docstrings to generate
    help messages and descriptions for each command and its arguments.

    Args:
        target_module (ModuleType): The module from which to retrieve functions
            for generating CLI commands.
        description (str): The description of the CLI tool.
        exclude_functions (list[str]): A list of function names to exclude from
            the CLI. Defaults to an empty list.

    Returns:
        argparse.ArgumentParser: A configured `argparse.ArgumentParser`
            instance for the CLI.

    Examples:
        >>> parser = _auto_generate_parser(
        ...     target_module=sys.modules[__name__],
        ...     description=__doc__ if __doc__ else __name__,
        ...     exclude_functions=["some_function", "another_function"],
        ... )
        >>> args = parser.parse_args()
        >>> if args.command:
        >>>     func = getattr(target_module, args.command)
        >>>     func_params = inspect.signature(func).parameters
        >>> func_args = {
        ...     k: v for k, v in vars(args).items() if k in func_params
        ... }
        >>>     func(**func_args)
        >>> else:
        >>>     parser.print_help()
    """

    # Create a command-line argument parser with a custom description, disabling
    # the default help option
    parser = argparse.ArgumentParser(description=f"{Fore.GREEN}{description}{Style.RESET_ALL}", add_help=False)

    # Add a custom help argument to the parser with a styled help message
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help=f"{Fore.CYAN}Show this help message and exit with the information on how to use this program.{Style.RESET_ALL}",
    )

    # Create subparsers for each command, allowing the CLI to handle different functions
    subparsers = parser.add_subparsers(dest="commands", title="commands")

    # Retrieve all functions from the target module that are not private (do not start with "_")
    functions = inspect.getmembers(target_module, inspect.isfunction)
    for name, func in functions:
        # Exclude private functions (starting with `_`) and user defined ones
        if not name.startswith("_") or name in exclude_functions:
            # Exclude functions decorated with `@lru_cache` by checking the function name and for
            # a `cache_info` attribute
            if name == "lru_cache" or hasattr(func, "cache_info"):
                continue

            # Parse the function's docstring to extract argument descriptions and other information
            parsed_docstring = _parse_docstring(func.__doc__ if func.__doc__ else "")

            # Use the first paragraph of the docstring as the description for the subparser (command)
            docstring_description = parsed_docstring["description"]
            subparser = subparsers.add_parser(
                name, help=f"{Fore.YELLOW}{docstring_description}{Style.RESET_ALL}", add_help=False
            )

            # Retrieve the function's parameters for further processing
            agruments = inspect.signature(func).parameters

            # Add a custom help option to each subparser (command) with a styled help message
            subparser.add_argument(
                "-h",
                "--help",
                action="help",
                default=argparse.SUPPRESS,
                help=f"{Fore.CYAN}Show this help message and exit with the information on how to use this command.{Style.RESET_ALL}",
            )

            # Iterate over the function's parameters to add them as arguments to the subparser
            for argument_name, argument in agruments.items():
                # Use the description from the parsed docstring if available, otherwise use a
                # generic description
                argument_help = (
                    parsed_docstring["args"].get(argument_name, {}).get("description", f"The {argument_name}")
                )

                # ! List
                # Check if the parameter is expected to be a list of strings
                if argument.annotation == list[str]:

                    def list_str(value):
                        return value.split(",")

                    # Required list argument
                    if argument.default is argument.empty:
                        subparser.add_argument(
                            argument_name,
                            type=list_str,
                            help=f"{Fore.YELLOW} ({argument.annotation.__name__}) {argument_help}{Style.RESET_ALL}",
                        )

                    # Optional list argument
                    else:
                        subparser.add_argument(
                            f"-{''.join(part[0] for part in argument_name.split('_') if part)}",
                            f"--{argument_name}",
                            type=list_str,
                            default=argument.default,
                            help=f"{Fore.CYAN}{argument_help} (default: {argument.default}){Style.RESET_ALL}",
                        )

                # ! Others
                # Handle non-list types
                else:
                    # Required argument
                    if argument.default is argument.empty:
                        subparser.add_argument(
                            argument_name,
                            type=argument.annotation,
                            help=f"{Fore.YELLOW} ({argument.annotation.__name__}) {argument_help}{Style.RESET_ALL}",
                        )

                    # Optional argument
                    else:
                        subparser.add_argument(
                            f"-{''.join(part[0] for part in argument_name.split('_') if part)}",
                            f"--{argument_name}",
                            type=argument.annotation,
                            default=argument.default,
                            help=f"{Fore.CYAN}{argument_help} (default: {argument.default}){Style.RESET_ALL}",
                        )
    return parser


def _print_ascii_art():
    """Prints the ASCII art for the CLI tool."""

    ascii_art = f"""
 .--.                  _
: .-'                 :_;
: `;.-.,-. .---..-..-..-.,-.,-. .--. .-.,-.
: : `.  .'' .; :: :; :: :: ,. :' .; :`.  .'
:_; :_,._;`._. ;`.__.':_;:_;:_;`.__.':_,._;
             : :
             :_:                     v{fxenvironment.FXQUINOX_VERSION}

    """

    print(f"{Fore.CYAN}{ascii_art}{Style.RESET_ALL}")


def main(
    target_module: ModuleType, description: str, exclude_functions: list[str] = [], print_title: bool = False
) -> None:
    """Generates the parsers for a CLI usage.

    Args:
        target_module (ModuleType): The module to be processed.
        description (str): The description of the CLI tool.
        exclude_functions (list[str]): A list of function names to exclude from
            the CLI. Defaults to an empty list.
        print_title (bool): Whether to print the ASCII art title. Defaults to
            `False`.

    Examples:
        In the target module
        >>> if __name__ == "__main__":
        >>>     from fxquinox import _fxcli
        >>>     _fxcli.main(
        ...         target_module=sys.modules[__name__],
        ...         description=__doc__ if __doc__ else __name__
        ...         exclude_functions=["some_function", "another_function"],
        ...         print_title=True
        ...     )
    """

    if print_title:
        _print_ascii_art()

    parser = _auto_generate_parser(target_module, description, exclude_functions)
    args = parser.parse_args()
    if args.commands:
        func = getattr(target_module, args.commands)
        func_params = inspect.signature(func).parameters
        func_args = {k: v for k, v in vars(args).items() if k in func_params}
        func(**func_args)
    else:
        parser.print_help()
