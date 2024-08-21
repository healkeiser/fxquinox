# Built-in
import json
import os
from pathlib import Path, WindowsPath

# Third-party
from qtpy import QtWidgets
import hou

# Internal
from fxquinox import fxlog, fxfiles, fxenvironment


# Log
_logger = fxlog.get_logger("houdini.contextoptions")
_logger.setLevel(fxlog.DEBUG)


def refresh_context_options_editor() -> None:
    """Refresh the context options editor."""

    editors = [
        widget
        for widget in QtWidgets.QApplication.instance().allWidgets()
        if str(type(widget)) == "<class 'contextoptions.OptionsEditor'>"
    ]
    for editor in editors:
        editor.reload()


def set_context_options():
    # Heading
    context_option_name = "fxquinox_heading"
    context_option_config = {
        "label": "Fxquinox",
        "type": "heading",
        "order": 9,
        "comment": "",
        "menu_items": [],
        "autovalues": False,
        "menu_source": "",
        "minimum": 0.0,
        "maximum": 10.0,
        "min_locked": False,
        "max_locked": False,
        "hidden": False,
    }
    hou.setContextOption(context_option_name, "")
    hou.setContextOptionConfig(
        context_option_name, json.dumps(context_option_config)
    )

    # Project
    context_option_name = "fxquinox_project"
    context_option_config = {
        "label": "Project",
        "type": "text",
        "order": 10,
        "comment": "",
        "menu_items": [],
        "autovalues": False,
        "menu_source": "",
        "minimum": 0,
        "maximum": 10,
        "min_locked": False,
        "max_locked": False,
        "hidden": False,
    }
    hou.setContextOption(
        context_option_name, os.getenv("FXQUINOX_PROJECT_NAME", "")
    )
    hou.setContextOptionConfig(
        context_option_name, json.dumps(context_option_config)
    )
    _logger.debug(
        f"{context_option_name}: {hou.contextOption(context_option_name)}"
    )

    # Project root
    context_option_name = "fxquinox_project_root"
    context_option_config = {
        "label": "Project Root",
        "type": "text",
        "order": 20,
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
    hou.setContextOption(
        context_option_name, os.getenv("FXQUINOX_PROJECT_ROOT", "")
    )
    hou.setContextOptionConfig(
        context_option_name, json.dumps(context_option_config)
    )
    _logger.debug(
        f"{context_option_name}: {hou.contextOption(context_option_name)}"
    )

    # Entity
    context_option_name = "fxquinox_entity"
    context_option_config = {
        "label": "Entity",
        "type": "string_menu",
        "order": 30,
        "comment": "",
        "menu_items": [["Asset", "Asset"], ["Shot", "Shot"]],
        "autovalues": True,
        "menu_source": "",
        "minimum": 0,
        "maximum": 10,
        "min_locked": False,
        "max_locked": False,
        "hidden": False,
    }

    hou.setContextOption(
        context_option_name, os.getenv("FXQUINOX_ENTITY", "Shot")
    )
    hou.setContextOptionConfig(
        context_option_name, json.dumps(context_option_config)
    )
    _logger.debug(
        f"{context_option_name}: {hou.contextOption(context_option_name)}"
    )

    # Asset
    context_option_name = "fxquinox_asset"
    context_option_python = (
        "import os\n"
        "from pathlib import Path\n\n"
        "asset_root = os.getenv('FXQUINOX_PROJECT_ASSETS_PATH')\n"
        "if not asset_root:\n"
        "    return []\n"
        "assets = [(asset.name, asset.name) for asset in Path(asset_root).iterdir() if asset.is_dir()]\n"
        "return assets\n"
    )
    context_option_config = {
        "label": "Asset",
        "type": "py_menu",
        "order": 40,
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
    hou.setContextOption(context_option_name, os.getenv("FXQUINOX_ASSET", ""))
    hou.setContextOptionConfig(
        context_option_name, json.dumps(context_option_config)
    )
    _logger.debug(
        f"{context_option_name}: {hou.contextOption(context_option_name)}"
    )

    # Sequence
    context_option_name = "fxquinox_sequence"
    context_option_python = (
        "import os\n"
        "from pathlib import Path\n\n"
        "project_shots_path = os.getenv('FXQUINOX_PROJECT_SHOTS_PATH')\n"
        "if not project_shots_path:\n"
        "    return []\n"
        "sequences = [(sequence.name, sequence.name) for sequence in Path(project_shots_path).iterdir() if sequence.is_dir()]\n"
        "return sequences\n"
    )
    context_option_config = {
        "label": "Sequence",
        "type": "py_menu",
        "order": 50,
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
    hou.setContextOption(
        context_option_name, os.getenv("FXQUINOX_SEQUENCE", "")
    )
    hou.setContextOptionConfig(
        context_option_name, json.dumps(context_option_config)
    )
    _logger.debug(
        f"{context_option_name}: {hou.contextOption(context_option_name)}"
    )

    # Shot
    context_option_name = "fxquinox_shot"
    context_option_python = (
        "import os\n"
        "from pathlib import Path\n"
        "import hou\n\n"
        "project_shots_path = os.getenv('FXQUINOX_PROJECT_SHOTS_PATH', '')\n"
        "if not project_shots_path:\n"
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
        "order": 60,
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
    hou.setContextOptionConfig(
        context_option_name, json.dumps(context_option_config)
    )
    _logger.debug(
        f"{context_option_name}: {hou.contextOption(context_option_name)}"
    )

    # # Step
    # context_option_name = "fxquinox_step"
    # context_option_python = (
    #     "import os\n"
    #     "from pathlib import Path\n"
    #     "import hou\n\n"
    #     "shot_root = os.getenv('FXQUINOX_PROJECT_SHOTS_PATH', '')\n"
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
    #     "shot_root = os.getenv('FXQUINOX_PROJECT_SHOTS_PATH', '')\n"
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
        "type": "int_slider",
        "order": 70,
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

    project_shots = os.getenv("FXQUINOX_PROJECT_SHOTS_PATH", "")
    sequence = hou.contextOption("fxquinox_sequence")
    shot = hou.contextOption("fxquinox_shot")
    if project_shots and sequence and shot:
        shot_path = Path(project_shots) / sequence / shot
        hou.setContextOption(
            context_option_name,
            fxfiles.get_metadata(shot_path.resolve().as_posix(), "cut_in"),
        )
    else:
        hou.setContextOption(context_option_name, 1001)
    hou.setContextOptionConfig(
        context_option_name, json.dumps(context_option_config)
    )
    _logger.debug(
        f"{context_option_name}: {hou.contextOption(context_option_name)}"
    )

    # Cut out
    context_option_name = "fxquinox_cut_out"
    context_option_config = {
        "label": "Cut Out",
        "type": "int_slider",
        "order": 80,
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

    project_shots = os.getenv("FXQUINOX_PROJECT_SHOTS_PATH", "")
    sequence = hou.contextOption("fxquinox_sequence")
    shot = hou.contextOption("fxquinox_shot")
    if project_shots and sequence and shot:
        shot_path = Path(project_shots) / sequence / shot
        hou.setContextOption(
            context_option_name,
            fxfiles.get_metadata(shot_path.resolve().as_posix(), "cut_out"),
        )
    else:
        hou.setContextOption(context_option_name, 1100)

    hou.setContextOptionConfig(
        context_option_name, json.dumps(context_option_config)
    )
    _logger.debug(
        f"{context_option_name}: {hou.contextOption(context_option_name)}"
    )


def _entity_callback(context_option: str):
    """Callback to execute when changing the entity context option.

    Args:
        context_option (str): The context option to check.
    """

    if not context_option == "fxquinox_entity":
        return

    context_option_value = hou.contextOption(context_option) or ""
    os.environ["FXQUINOX_ENTITY"] = context_option_value
    _logger.debug(f"{context_option}: {context_option_value}")


def _sequence_callback(context_option: str):
    """Callback to  execute when changing the sequence context option.

    Args:
        context_option (str): The context option to check.
    """

    if not context_option == "fxquinox_sequence":
        return

    context_option_value = hou.contextOption(context_option) or ""
    os.environ["FXQUINOX_SEQUENCE"] = context_option_value

    if context_option_value != None and context_option_value != "":
        path_sequence: Path = (
            Path(os.getenv("FXQUINOX_PROJECT_SHOTS_PATH", ""))
            / context_option_value
        )
        os.environ["FXQUINOX_SEQUENCE_PATH"] = (
            path_sequence.resolve().as_posix()
        )

    _logger.debug(f"{context_option}: {context_option_value}")


def _shot_callback(context_option: str):
    """Callback to  execute when changing the shot context option.

    Args:
        context_option (str): The context option to check.
    """

    if not context_option == "fxquinox_shot":
        return

    context_option_value = hou.contextOption(context_option) or ""
    os.environ["FXQUINOX_SHOT"] = context_option_value

    sequence = hou.contextOption("fxquinox_sequence")

    if context_option_value and sequence:
        path_shot: Path = (
            Path(os.getenv("FXQUINOX_PROJECT_SHOTS_PATH", ""))
            / sequence
            / context_option_value
        )
        os.environ["FXQUINOX_SHOT_PATH"] = path_shot.resolve().as_posix()

    _logger.debug(f"{context_option}: {context_option_value}")


def add_context_options_callbacks() -> None:
    """Add callbacks on the context options."""

    hou.addContextOptionChangeCallback(_entity_callback)
    _logger.debug(
        f"Added context option change callback: {_entity_callback.__name__}"
    )
    hou.addContextOptionChangeCallback(_sequence_callback)
    _logger.debug(
        f"Added context option change callback: {_sequence_callback.__name__}"
    )
    hou.addContextOptionChangeCallback(_shot_callback)
    _logger.debug(
        f"Added context option change callback: {_shot_callback.__name__}"
    )
