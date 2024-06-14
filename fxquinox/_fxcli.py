# Built-in
import argparse
from functools import WRAPPER_ASSIGNMENTS
import inspect
import re
from types import ModuleType


def _parse_docstring(docstring: str) -> dict:
    """Parses the docstring to find parameter descriptions.

    Args:
        docstring (str): The docstring from which to extract parameter descriptions.

    Returns:
        dict: A dictionary where keys are parameter names and values are their descriptions.
    """

    # Isolate the `Args` section of the docstring
    args_section_match = re.search(r"Args:\n\s*(.*?)(?=\n\s*\n)", docstring, re.DOTALL)
    if not args_section_match:
        return {}

    args_section = args_section_match.group(1)

    # Split arguments and extract names and descriptions
    arg_descriptions = {}
    arg_lines = re.finditer(r"(\w+)\s*\(.*?\):\s*(.*?)\s*(?=\w+\s*\(|$)", args_section, re.DOTALL)
    for match in arg_lines:
        arg_name = match.group(1)
        arg_description = match.group(2).replace("\n", " ").strip()
        arg_descriptions[arg_name] = arg_description

    return arg_descriptions


def _auto_generate_parser(target_module: ModuleType, description: str) -> argparse.ArgumentParser:
    """Automatically generates an argparse parser based on the functions defined in the given module.
    It uses function docstrings to generate help messages and descriptions for each command and its arguments.s.

    Args:
        target_module (ModuleType): The module from which to retrieve functions for generating CLI commands.
        description (str): The description of the CLI tool.

    Returns:
        argparse.ArgumentParser: A configured `argparse.ArgumentParser` instance for the CLI.
    """

    parser = argparse.ArgumentParser(description=description, add_help=False)

    # Custom help message for parser (tool)
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit with the information on how to use this program.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Retrieve all functions in the current module
    functions = inspect.getmembers(target_module, inspect.isfunction)
    for name, func in functions:
        if not name.startswith("_"):  # Filter out private functions

            # Skip functions decorated with `@lru_cache` by checking for the cache_info attribute
            if name == "lru_cache" or hasattr(func, "cache_info"):
                continue

            # Additional check for `functools.wraps` decorated functions
            if any(hasattr(func, attr) for attr in WRAPPER_ASSIGNMENTS):
                original_func = getattr(func, "__wrapped__", None)
                if original_func and hasattr(original_func, "cache_info"):
                    continue

            # Use the first paragraph of the docstring as the command description
            func_help = func.__doc__.split("\n\n")[0] if func.__doc__ else "No description available."
            subparser = subparsers.add_parser(name, help=func_help, add_help=False)

            # Parse the docstring for argument descriptions
            arg_descriptions = _parse_docstring(func.__doc__)
            params = inspect.signature(func).parameters

            # Custom help option for subparser (commands)
            subparser.add_argument(
                "-h",
                "--help",
                action="help",
                default=argparse.SUPPRESS,
                help="Show this help message and exit with the information on how to use this command.",
            )

            for param_name, param in params.items():

                # Use the parsed docstring description if available, otherwise use a generic message
                arg_help = arg_descriptions.get(param_name, f"The {param_name}")

                # Required argument
                if param.default is param.empty:
                    subparser.add_argument(param_name, type=str, help=arg_help)

                # Optional argument
                else:
                    subparser.add_argument(
                        f"--{param_name}",
                        type=str,
                        default=param.default,
                        help=f"{arg_help} (default: {param.default})",
                    )

    return parser


def main(target_module: ModuleType, description: str) -> None:
    """Executes the main functionality of the script, generating the parsers for a CLI usage.

    Args:
        target_module (ModuleType): The module to be processed.
        description (str): The description of the CLI tool.
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