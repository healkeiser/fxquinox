"""Allows to automatically generate CLI tools from Python modules.

Examples:
    Set up the CLI in an external Python module
    >>> if __name__ == "__main__":
    >>>     from fxquinox import _fxcli
    >>>     _fxcli.main(target_module=sys.modules[__name__], description=__doc__ if __doc__ else __name__)

    Run the CLI tool in the terminal
    >>> python -m fxquinox.fxcore -h
    usage: fxcore.py [-h] {create_asset,create_project,create_sequence,create_shot} ...
"""

# Built-in
import argparse
import inspect
import json
import re
from types import ModuleType

# Third-party
from colorama import just_fix_windows_console, Fore, Style


# Initialize colorama
just_fix_windows_console()


def _parse_docstring(docstring):
    """Parses a docstring into its components: description, arguments, and
        return type, supporting multiline descriptions.

    Args:
        docstring (str): The docstring to parse.

    Returns:
        dict: A dictionary with 'description', 'args', and 'returns' keys.
    """

    parsed = {"description": "", "args": {}, "returns": None}

    # Split the docstring into lines and strip leading/trailing whitespace
    lines = [line.strip() for line in docstring.split("\n")]

    current_section = "description"
    current_arg = None

    for line in lines:
        if line.startswith("Args:"):
            current_section = "args"
            continue
        elif line.startswith("Returns:"):
            current_section = "returns"
            continue

        if current_section == "description":
            parsed["description"] += " " + line if parsed["description"] else line
        elif current_section == "args":
            arg_match = re.match(r"^(\w+) \((\w+)\): (.+)$", line)
            if arg_match:
                current_arg = arg_match.group(1)
                arg_type = arg_match.group(2)
                arg_desc = arg_match.group(3)
                parsed["args"][current_arg] = {"type": arg_type, "description": arg_desc}
            elif current_arg:
                # Append to the last argument's description if it's a multiline description
                parsed["args"][current_arg]["description"] += " " + line
        elif current_section == "returns":
            if "type" not in parsed["returns"]:  # First line after "Returns:" is the return info
                returns_match = re.match(r"^(\w+): (.+)$", line)
                if returns_match:
                    return_type = returns_match.group(1)
                    return_desc = returns_match.group(2)
                    parsed["returns"] = {"type": return_type, "description": return_desc}
            else:
                # Append to the return description if it's a multiline description
                parsed["returns"]["description"] += " " + line

    return parsed


def _auto_generate_parser(target_module: ModuleType, description: str) -> argparse.ArgumentParser:
    """Automatically generates an argparse parser based on the functions defined in the given module.
    It uses function docstrings to generate help messages and descriptions for each command and its arguments.s.

    Args:
        target_module (ModuleType): The module from which to retrieve functions for generating CLI commands.
        description (str): The description of the CLI tool.

    Returns:
        argparse.ArgumentParser: A configured `argparse.ArgumentParser` instance for the CLI.

    Examples:
        >>> parser = _auto_generate_parser(target_module=sys.modules[__name__], description=__doc__ if __doc__ else __name__)
        >>> args = parser.parse_args()
        >>> if args.command:
        >>>     func = getattr(target_module, args.command)
        >>>     func_params = inspect.signature(func).parameters
        >>>     func_args = {k: v for k, v in vars(args).items() if k in func_params}
        >>>     func(**func_args)
        >>> else:
        >>>     parser.print_help()
    """

    parser = argparse.ArgumentParser(description=f"{Fore.GREEN}{description}{Style.RESET_ALL}", add_help=False)

    # Custom help message for parser (tool)
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help=f"{Fore.CYAN}Show this help message and exit with the information on how to use this program.{Style.RESET_ALL}",
    )
    subparsers = parser.add_subparsers(dest="command", title="Functions")

    # Retrieve all functions in the target module
    functions = inspect.getmembers(target_module, inspect.isfunction)
    for name, func in functions:
        if not name.startswith("_"):  # Filter out private functions
            # Skip functions decorated with `@lru_cache` by checking for the name and
            # `cache_info` attribute
            if name == "lru_cache" or hasattr(func, "cache_info"):
                continue

            # Parse the docstring for argument descriptions
            parsed_docstring = _parse_docstring(func.__doc__ if func.__doc__ else "")

            # Use the first paragraph of the docstring as the command description
            docstring_description = parsed_docstring["description"]
            subparser = subparsers.add_parser(
                name, help=f"{Fore.YELLOW}{docstring_description}{Style.RESET_ALL}", add_help=False
            )

            # print(json.dumps(parsed_docstring, indent=4, sort_keys=True))
            params = inspect.signature(func).parameters

            # Custom help option for subparser (commands)
            subparser.add_argument(
                "-h",
                "--help",
                action="help",
                default=argparse.SUPPRESS,
                help=f"{Fore.CYAN}Show this help message and exit with the information on how to use this command.{Style.RESET_ALL}",
            )

            for param_name, param in params.items():

                # Use the parsed docstring description if available, otherwise use a generic message
                arg_help = parsed_docstring["args"].get(param_name, {}).get("description", f"The {param_name}")

                # Check if the parameter is expected to be a list of strings
                if param.annotation == list[str]:

                    def list_str(value):
                        return value.split(",")

                    # Required list argument
                    if param.default is param.empty:
                        subparser.add_argument(
                            param_name,
                            type=list_str,
                            help=f"{Fore.YELLOW} ({param.annotation.__name__}) {arg_help}{Style.RESET_ALL}",
                        )

                    # Optional list argument
                    else:
                        subparser.add_argument(
                            f"-{''.join(part[0] for part in param_name.split('_') if part)}",
                            f"--{param_name}",
                            type=list_str,
                            default=param.default,
                            help=f"{Fore.CYAN}{arg_help} (default: {param.default}){Style.RESET_ALL}",
                        )

                # Handle non-list types
                else:
                    # Required argument
                    if param.default is param.empty:
                        subparser.add_argument(
                            param_name,
                            type=param.annotation,
                            help=f"{Fore.YELLOW} ({param.annotation.__name__}) {arg_help}{Style.RESET_ALL}",
                        )

                    # Optional argument
                    else:
                        subparser.add_argument(
                            f"-{''.join(part[0] for part in param_name.split('_') if part)}",
                            f"--{param_name}",
                            type=param.annotation,
                            default=param.default,
                            help=f"{Fore.CYAN}{arg_help} (default: {param.default}){Style.RESET_ALL}",
                        )
    return parser


def main(target_module: ModuleType, description: str) -> None:
    """Executes the main functionality of the script, generating the parsers for a CLI usage.

    Args:
        target_module (ModuleType): The module to be processed.
        description (str): The description of the CLI tool.

    Examples:
        >>> if __name__ == "__main__":
        >>>     from fxquinox import _fxcli
        >>>     _fxcli.main(target_module=sys.modules[__name__], description=__doc__ if __doc__ else __name__)
    """

    parser = _auto_generate_parser(target_module, description)
    args = parser.parse_args()
    if args.command:
        func = getattr(target_module, args.command)
        func_params = inspect.signature(func).parameters
        func_args = {k: v for k, v in vars(args).items() if k in func_params}
        func(**func_args)
    else:
        parser.print_help()
