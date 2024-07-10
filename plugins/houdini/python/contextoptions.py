# Built-in
import json
import os
from pathlib import Path

# Third-party
import hou

# Internal
from fxquinox import fxlog, fxfiles


# Log
_logger = fxlog.get_logger("houdini.contextoptions")
_logger.setLevel(fxlog.DEBUG)


def set_context_options():
    # Project
    context_option_name = "fxquinox_project"
    context_option_config = {
        "label": "Project",
        "type": "text",
        "order": 1,
        "comment": "",
        "menu_items": [],
        "autovalues": False,
        "menu_source": "",
        "minimum": 0,
        "maximum": 10,
        "min_locked": False,
        "max_locked": False,
        "hidden": True,
    }
    hou.setContextOption(context_option_name, os.getenv("FXQUINOX_PROJECT_NAME", ""))
    hou.setContextOptionConfig(context_option_name, json.dumps(context_option_config))
    _logger.debug(f"{context_option_name}: {hou.contextOption(context_option_name)}")

    # Project root
    context_option_name = "fxquinox_project_root"
    context_option_config = {
        "label": "Project Root",
        "type": "text",
        "order": 2,
        "comment": "",
        "menu_items": [],
        "autovalues": False,
        "menu_source": "",
        "minimum": 0,
        "maximum": 10,
        "min_locked": False,
        "max_locked": False,
        "hidden": True,
    }
    hou.setContextOption(context_option_name, os.getenv("FXQUINOX_PROJECT_ROOT", ""))
    hou.setContextOptionConfig(context_option_name, json.dumps(context_option_config))
    _logger.debug(f"{context_option_name}: {hou.contextOption(context_option_name)}")

    # Sequence
    context_option_name = "fxquinox_sequence"
    context_option_python = (
        "import os\n"
        "from pathlib import Path\n\n"
        "shot_root = os.getenv('FXQUINOX_PROJECT_SHOTS')\n"
        "if not shot_root:\n"
        "    return []\n"
        "sequences = [(sequence.name, sequence.name) for sequence in Path(shot_root).iterdir() if sequence.is_dir()]\n"
        "return sequences\n"
    )
    context_option_config = {
        "label": "Sequence",
        "type": "py_menu",
        "order": 3,
        "comment": "",
        "menu_items": [],
        "autovalues": True,
        "menu_source": context_option_python,
        "minimum": 0,
        "maximum": 10,
        "min_locked": False,
        "max_locked": False,
        "hidden": False,
    }
    hou.setContextOption(context_option_name, os.getenv("FXQUINOX_SEQUENCE", ""))
    hou.setContextOptionConfig(context_option_name, json.dumps(context_option_config))
    _logger.debug(f"{context_option_name}: {hou.contextOption(context_option_name)}")

    # Shot
    context_option_name = "fxquinox_shot"
    context_option_python = (
        "import os\n"
        "from pathlib import Path\n"
        "import hou\n\n"
        "shot_root = os.getenv('FXQUINOX_PROJECT_SHOTS', '')\n"
        "if not shot_root:\n"
        "    return []\n"
        "sequence = hou.contextOption('fxquinox_sequence')\n"
        "path_shot_root = Path(shot_root)\n"
        "path_sequence = path_shot_root / sequence\n"
        "shots = [(shot.name, shot.name) for shot in Path(path_sequence).iterdir() if shot.is_dir()]\n"
        "return shots\n"
    )
    context_option_config = {
        "label": "Shot",
        "type": "py_menu",
        "order": 4,
        "comment": "",
        "menu_items": [],
        "autovalues": True,
        "menu_source": context_option_python,
        "minimum": 0,
        "maximum": 10,
        "min_locked": False,
        "max_locked": False,
        "hidden": False,
    }
    hou.setContextOption(context_option_name, os.getenv("FXQUINOX_SHOT", ""))
    hou.setContextOptionConfig(context_option_name, json.dumps(context_option_config))
    _logger.debug(f"{context_option_name}: {hou.contextOption(context_option_name)}")

    # # Step
    # context_option_name = "fxquinox_step"
    # context_option_python = (
    #     "import os\n"
    #     "from pathlib import Path\n"
    #     "import hou\n\n"
    #     "shot_root = os.getenv('FXQUINOX_PROJECT_SHOTS', '')\n"
    #     "if not shot_root:\n"
    #     "    return []\n"
    #     "sequence = hou.contextOption('fxquinox_sequence')\n"
    #     "shot = hou.contextOption('fxquinox_shot')\n"
    #     "path_shot_root = Path(shot_root)\n"
    #     "path_sequence = path_shot_root / sequence\n"
    #     "path_shot = path_sequence / shot\n"
    #     "path_workfiles = path_shot / 'workfiles'\n"
    #     "steps = [(step.name, step.name) for step in Path(path_workfiles).iterdir() if step.is_dir()]\n"
    #     "return steps\n"
    # )
    # context_option_config = {
    #     "label": "Step",
    #     "type": "py_menu",
    #     "order": 5,
    #     "comment": "",
    #     "menu_items": [],
    #     "autovalues": True,
    #     "menu_source": context_option_python,
    #     "minimum": 0,
    #     "maximum": 10,
    #     "min_locked": False,
    #     "max_locked": False,
    #     "hidden": False,
    # }
    # hou.setContextOption(context_option_name, os.getenv("FXQUINOX_STEP", ""))
    # hou.setContextOptionConfig(context_option_name, json.dumps(context_option_config))
    # _logger.debug(f"{context_option_name}: {hou.contextOption(context_option_name)}")

    # # Task
    # context_option_name = "fxquinox_task"
    # context_option_python = (
    #     "import os\n"
    #     "from pathlib import Path\n"
    #     "import hou\n\n"
    #     "shot_root = os.getenv('FXQUINOX_PROJECT_SHOTS', '')\n"
    #     "if not shot_root:\n"
    #     "    return []\n"
    #     "sequence = hou.contextOption('fxquinox_sequence')\n"
    #     "shot = hou.contextOption('fxquinox_shot')\n"
    #     "step = hou.contextOption('fxquinox_step')\n"
    #     "path_shot_root = Path(shot_root)\n"
    #     "path_sequence = path_shot_root / sequence\n"
    #     "path_shot = path_sequence / shot\n"
    #     "path_workfiles = path_shot / 'workfiles'\n"
    #     "path_step = path_workfiles / step\n"
    #     "tasks = [(task.name, task.name) for task in Path(path_step).iterdir() if task.is_dir()]\n"
    #     "return tasks\n"
    # )
    # context_option_config = {
    #     "label": "Task",
    #     "type": "py_menu",
    #     "order": 6,
    #     "comment": "",
    #     "menu_items": [],
    #     "autovalues": True,
    #     "menu_source": context_option_python,
    #     "minimum": 0,
    #     "maximum": 10,
    #     "min_locked": False,
    #     "max_locked": False,
    #     "hidden": False,
    # }
    # hou.setContextOption(context_option_name, os.getenv("FXQUINOX_TASK", ""))
    # hou.setContextOptionConfig(context_option_name, json.dumps(context_option_config))
    # _logger.debug(f"{context_option_name}: {hou.contextOption(context_option_name)}")

    # Cut in
    context_option_name = "fxquinox_cut_in"
    context_option_config = {
        "label": "Cut In",
        "type": "int",
        "order": 7,
        "comment": "",
        "menu_items": [],
        "autovalues": False,
        "menu_source": "",
        "minimum": 0,
        "maximum": 10000,
        "min_locked": False,
        "max_locked": False,
        "hidden": False,
    }
    hou.setContextOption(context_option_name, "1001")
    # hou.setContextOptionConfig(context_option_name, json.dumps(context_option_config))
    _logger.debug(f"{context_option_name}: {hou.contextOption(context_option_name)}")

    # Cut out
    context_option_name = "fxquinox_cut_out"
    context_option_config = {
        "label": "Cut Out",
        "type": "int",
        "order": 8,
        "comment": "",
        "menu_items": [],
        "autovalues": False,
        "menu_source": "",
        "minimum": 0,
        "maximum": 10000,
        "min_locked": False,
        "max_locked": False,
        "hidden": False,
    }
    hou.setContextOption(context_option_name, "1100")
    # hou.setContextOptionConfig(context_option_name, json.dumps(context_option_config))
    _logger.debug(f"{context_option_name}: {hou.contextOption(context_option_name)}")


def _sequence_callback(context_option: str):
    """Callback to  execute when changing the sequence context option.

    Args:
        context_option (str): The context option to check.
    """

    if not context_option == "fxquinox_sequence":
        return

    context_option_value = hou.contextOption(context_option)
    _logger.debug(f"{context_option}: {context_option_value}")


def _shot_callback(context_option: str):
    """Callback to  execute when changing the shot context option.

    Args:
        context_option (str): The context option to check.
    """

    if not context_option == "fxquinox_shot":
        return

    context_option_value = hou.contextOption(context_option)
    _logger.debug(f"{context_option}: {context_option_value}")
    project_shots = os.getenv("FXQUINOX_PROJECT_SHOTS", "")
    sequence = hou.contextOption("fxquinox_sequence")
    shot = hou.contextOption("fxquinox_shot")

    if not project_shots or not sequence or not shot:
        return

    path_shot = Path(project_shots) / sequence / shot

    cut_in_str = fxfiles.get_metadata(file_path=path_shot.resolve().as_posix(), metadata_name="cut_in")
    if cut_in_str:
        hou.setContextOption("fxquinox_cut_in", int(cut_in_str))

    cut_out_str = fxfiles.get_metadata(file_path=path_shot.resolve().as_posix(), metadata_name="cut_out")
    if cut_out_str:
        hou.setContextOption("fxquinox_cut_out", int(cut_out_str))


def add_context_options_callbacks() -> None:
    """Add callbacks on the context options."""

    hou.addContextOptionChangeCallback(_sequence_callback)
    _logger.debug(f"Added context option change callback: {_sequence_callback.__name__}")
    hou.addContextOptionChangeCallback(_shot_callback)
    _logger.debug(f"Added context option change callback: {_shot_callback.__name__}")
