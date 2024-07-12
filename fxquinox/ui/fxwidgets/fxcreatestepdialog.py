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
_logger = fxlog.get_logger("fxcreatestepdialog")
_logger.setLevel(fxlog.DEBUG)


class FXCreateStepDialog(QDialog):
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

        # Methods
        self.setModal(True)

        self._create_ui()
        self._rename_ui()
        self._modify_ui()
        self._handle_connections()
        self._populate_steps()

        _logger.info("Initialized create step")

    def _create_ui(self):
        """_summary_"""

        ui_file = Path(fxenvironment._FXQUINOX_UI) / "create_step.ui"
        self.ui = fxguiutils.load_ui(self, str(ui_file))
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)
        self.setWindowTitle(f"Create Step | {self.sequence} - {self.shot}")

    def _rename_ui(self):
        """_summary_"""

        self.list_steps: QListWidget = self.ui.list_steps
        self.checkbox_add_tasks: QCheckBox = self.ui.checkbox_add_tasks
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
                # Create step
                button.clicked.connect(self._create_step)
            elif role == QDialogButtonBox.RejectRole:
                button.setIcon(fxicons.get_icon("close", color="#ec0811"))
                # Close
                button.clicked.connect(self.close)

    def _handle_connections(self):
        """_summary_"""

        self.list_steps.currentItemChanged.connect(self._populate_tasks)
        self.checkbox_add_tasks.stateChanged.connect(
            lambda: self.list_tasks.setEnabled(self.checkbox_add_tasks.isChecked())
        )

    def _populate_steps(self):
        # Parse the `steps.yaml` file
        steps_file = Path(self._project_root) / ".pipeline" / "project_config" / "steps.yaml"
        if not steps_file.exists():
            return
        steps_data = yaml.safe_load(steps_file.read_text())

        # Gather existing step names
        parent = self.parent()
        if parent:
            existing_steps = {parent.list_steps.item(i).text() for i in range(parent.list_steps.count())}
        else:
            existing_steps = []

        for step in steps_data["steps"]:
            step_name = step.get("name_long", "Unknown Step")
            if step_name not in existing_steps:
                step_item = QListWidgetItem(step_name)
                step_item.setIcon(
                    fxicons.get_icon(step.get("icon", "check_box_outline_blank"), color=step.get("color", "#ffffff"))
                )
                step_item.setData(Qt.UserRole, step)
                self.list_steps.addItem(step_item)

    def _populate_tasks(self, current, previous):
        self.list_tasks.clear()  # Clear existing tasks
        if current is not None:
            step = current.data(Qt.UserRole)
            for task in step["tasks"]:
                task_item = QListWidgetItem(task.get("name", "Unknown Task"))
                task_item.setIcon(fxicons.get_icon("task_alt"))
                task_item.setData(Qt.UserRole, task)
                self.list_tasks.addItem(task_item)

    def _create_step(self):
        # Get the selected step
        _logger.debug(f"Asset: '{self.asset}', sequence: '{self.sequence}', shot: '{self.shot}'")
        step = self.list_steps.currentItem().text()

        # Create the step
        workfiles_dir = Path(self._project_root) / "production" / "shots" / self.sequence / self.shot / "workfiles"
        step = fxcore.create_step(step, workfiles_dir, self)
        if not step:
            return

        step_dir = workfiles_dir / step
        if self.checkbox_add_tasks.isChecked():
            for i in range(self.list_tasks.count()):
                task = self.list_tasks.item(i).text()
                fxcore.create_task(task, step_dir, self)

        # Refresh parent and close QDialog on completion
        parent = self.parent()
        if parent:
            parent.refresh()

        self.close()
