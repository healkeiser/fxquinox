# Built-in
from pathlib import Path

# Third-party
from fxgui import fxicons, fxutils as fxguiutils
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *
import yaml

# Internal
from fxquinox import fxcore, fxenvironment, fxlog

# Log
_logger = fxlog.get_logger("fxcreatetaskdialog")
_logger.setLevel(fxlog.DEBUG)


class FXCreateTaskDialog(QDialog):
    def __init__(
        self,
        parent=None,
        project_name=None,
        project_root=None,
        project_assets=None,
        project_shots=None,
        asset=None,
        sequence=None,
        shot=None,
        step=None,
    ):
        super().__init__(parent)

        # Attributes
        self.project_name = project_name
        self._project_root = project_root
        self._project_assets_path = project_assets
        self._project_shots_path = project_shots

        self.asset = asset
        self.sequence = sequence
        self.shot = shot
        self.step = step

        # Methods
        self.setModal(True)

        self._create_ui()
        self._rename_ui()
        self._modify_ui()
        self._populate_tasks()

        _logger.info("Initialized create task")

    def _create_ui(self):
        """_summary_"""

        ui_file = Path(fxenvironment._FXQUINOX_UI) / "create_task.ui"
        self.ui = fxguiutils.load_ui(self, str(ui_file))
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)
        self.setWindowTitle(
            f"Create Task | {self.sequence} - {self.shot} - {self.step}"
        )

    def _rename_ui(self):
        """_summary_"""

        self.list_tasks: QListWidget = self.ui.list_tasks
        self.button_box: QButtonGroup = self.ui.button_box

    def _modify_ui(self):
        # Contains some slots connections, to avoid iterating multiple times
        # over the buttons
        for button in self.button_box.buttons():
            role = self.button_box.buttonRole(button)
            if role == QDialogButtonBox.AcceptRole:
                button.setIcon(fxicons.get_icon("check", color="#8fc550"))
                button.setText("Create")
                # Create task
                button.clicked.connect(self._create_task)
            elif role == QDialogButtonBox.RejectRole:
                button.setIcon(fxicons.get_icon("close", color="#ec0811"))
                # Close
                button.clicked.connect(self.close)

    def _populate_tasks(self):
        self.list_tasks.clear()  # Clear existing tasks

        steps_file = (
            Path(self._project_root)
            / ".pipeline"
            / "project_config"
            / "steps.yaml"
        )
        if not steps_file.exists():
            return

        steps_data = yaml.safe_load(steps_file.read_text())

        # Find the step that matches self.step
        current_step = next(
            (
                step
                for step in steps_data["steps"]
                if step["name_long"] == self.step
            ),
            None,
        )
        if not current_step:
            return  # If the step is not found, exit the function

        # Gather existing task names
        parent = self.parent()
        if parent:
            existing_tasks = {
                parent.list_tasks.item(i).text()
                for i in range(parent.list_tasks.count())
            }
        else:
            existing_tasks = []

        # Iterate over the tasks of the found step
        for task in current_step.get("tasks", []):
            task_name = task.get("name", "Unknown Task")
            if (
                task_name not in existing_tasks
            ):  # Check if the task is not already in the list
                task_item = QListWidgetItem(task_name)
                task_item.setIcon(fxicons.get_icon("task_alt"))
                task_item.setData(Qt.UserRole, task)
                self.list_tasks.addItem(task_item)
                # existing_tasks.add(task_name)  # Add the new task name to the set of existing tasks

    def _create_task(self):
        # Get the selected task
        _logger.debug(
            f"Asset: '{self.asset}', sequence: '{self.sequence}', shot: '{self.shot}', step: '{self.step}'"
        )
        task = self.list_tasks.currentItem().text()

        # Create the task
        step_dir = (
            Path(self._project_root)
            / "production"
            / "shots"
            / self.sequence
            / self.shot
            / "workfiles"
            / self.step
        )
        task = fxcore.create_task(task, step_dir, self)
        if not task:
            return

        # Refresh parent and close QDialog on completion
        parent = self.parent()
        if parent:
            parent.refresh()

        self.close()
