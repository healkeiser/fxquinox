# Built-in
from pathlib import Path
import sys
import subprocess

# Third-party
from fxgui import fxwidgets, fxicons, fxstyle, fxutils as fxguiutils
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *
import yaml

# Internal
from fxquinox import fxenvironment, fxlog, fxutils, fxcore


# Log
_logger = fxlog.get_logger("fxquinox.fxcore")
_logger.setLevel(fxlog.DEBUG)


class _FXTempWidget(QWidget):
    """A temporary widget that will be linked to display the splashscreen, as
    we can't `splashcreen.finish()` without a QWidget."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGeometry(0, 0, 0, 0)
        self.hide()
        self.close()


class FXExecutableRunnerThread(QThread):
    """A QThread subclass to run an executable in a separate thread."""

    # Define a signal to emit upon completion, if needed
    finished = Signal()

    def __init__(self, executable, commands=None, parent=None):
        super(FXExecutableRunnerThread, self).__init__(parent)
        self.executable = executable
        self.commands = commands

    def run(self):
        if self.executable:
            call = ['"' + self.executable + '"'] + self.commands if self.commands else ['"' + self.executable + '"']
        else:
            # If executable is empty, ensure commands is not `None` or empty
            # before proceeding
            if self.commands:
                call = self.commands
            else:
                _logger.error("No executable or commands provided to run")
                self.finished.emit()
                return

        _logger.debug(f"Call: {call}")

        if sys.platform == "win32":
            # On Windows, use `start cmd.exe /k` to open a new command prompt
            # that stays open
            cmd = "start cmd.exe /k " + " ".join(call)
            subprocess.Popen(cmd, shell=True)
        else:
            # On Unix-like systems, we might need to specify a terminal
            # emulator.
            # For example, using `xterm`:
            # >>> cmd = ["xterm", "-e"] + call
            # >>> subprocess.Popen(cmd)
            # Or we can simply run the command in a new shell without keeping
            # the terminal open:
            _logger.debug(f"Call: {call}")
            subprocess.Popen(call, shell=True)

        self.finished.emit()


class FXLauncherSystemTray(fxwidgets.FXSystemTray):
    """The Fxuinox main launcher UI class.

    Args:
        parent (QWidget): The parent widget.
        icon (QIcon): The icon to display in the system tray.
        project (str): The current project name.

    Signals:
        project_changed (str, str): The signal emitted when the project is
            changed.

    Note:
        This class inherits from `FXSystemTray` which is a custom system tray
        class that inherits from `QSystemTrayIcon`.
    """

    project_changed = Signal(str, str)

    def __init__(self, parent=None, icon=None, project=None):
        super().__init__(parent, icon)

        # Attributes
        self.project = project

        _logger.debug(f"Launcher project: '{self.project}'")

        self.colors = fxstyle.load_colors_from_jsonc()
        self.runner_threads = []

        # Methods
        self.__create_actions()
        self._create_label()
        self._create_app_launcher(project_name=self.project)
        self.__handle_connections()
        self._update_label(project_name=self.project)
        self._toggle_action_state(project_name=self.project)

    # ! Double `__` to avoid name clashes with the parent class
    def __handle_connections(self) -> None:
        """Connects the signals to the slots."""

        self.project_changed.connect(self._update_label)
        self.project_changed.connect(self._toggle_action_state)
        self.project_changed.connect(self._load_and_display_apps)

    # ! Double `__` to avoid name clashes with the parent class
    def __create_actions(self) -> None:
        """Creates the actions for the system tray."""

        self.create_project_action = fxguiutils.create_action(
            self.tray_menu,
            "Create Project...",
            fxicons.get_icon("movie_filter"),
            lambda: fxcore.set_project(launcher=self),
        )

        self.set_project_action = fxguiutils.create_action(
            self.tray_menu,
            "Set Project",
            fxicons.get_icon("movie"),
            lambda: fxcore.set_project(launcher=self),
        )

        self.open_project_browser_action = fxguiutils.create_action(
            self.tray_menu,
            "Project Browser...",
            fxicons.get_icon("perm_media"),
            fxcore.run_project_browser,
        )

        self.open_project_directory_action = fxguiutils.create_action(
            self.tray_menu,
            "Open Project Directory...",
            fxicons.get_icon("open_in_new"),
            fxcore.open_project_directory,
        )

        #
        self.fxquinox_menu = QMenu("Fxquinox", self.tray_menu)
        self.fxquinox_menu.setIcon(QIcon(str(Path(__file__).parents[1] / "images" / "fxquinox_logo_light.svg")))

        self.open_fxquinox_appdata = fxguiutils.create_action(
            self.fxquinox_menu,
            "Open Application Data Directory...",
            fxicons.get_icon("open_in_new"),
            lambda: fxcore.open_directory(fxenvironment.FXQUINOX_APPDATA),
        )

        self.open_fxquinox_temp = fxguiutils.create_action(
            self.fxquinox_menu,
            "Open Temp Directory...",
            fxicons.get_icon("open_in_new"),
            lambda: fxcore.open_directory(fxenvironment.FXQUINOX_TEMP),
        )

        self.tray_menu.insertAction(self.quit_action, self.open_project_directory_action)
        self.tray_menu.insertAction(self.open_project_directory_action, self.open_project_browser_action)
        self.tray_menu.insertAction(self.open_project_browser_action, self.set_project_action)

        self.tray_menu.insertMenu(self.quit_action, self.fxquinox_menu)
        self.fxquinox_menu.addAction(self.open_fxquinox_appdata)
        self.fxquinox_menu.addAction(self.open_fxquinox_temp)

        self.tray_menu.insertSeparator(self.open_project_directory_action)
        self.tray_menu.insertSeparator(self.quit_action)

    def _create_label(self) -> None:
        """Creates the label for the system tray."""

        container_widget = QWidget()
        layout = QVBoxLayout(container_widget)
        self.label = QLabel(self.project)
        layout.addWidget(self.label)
        layout.setContentsMargins(10, 10, 10, 10)
        label_action = QWidgetAction(self.tray_menu)
        label_action.setDefaultWidget(container_widget)
        self.tray_menu.insertAction(self.set_project_action, label_action)
        self._set_label_style()

    def _create_app_launcher(self, project_root: str = None, project_name: str = None) -> None:
        """Creates the application launcher as a grid and adds a QLineEdit for additional arguments."""
        container_widget = QWidget()
        container_widget.setObjectName("app_launcher_container")
        container_widget.setStyleSheet(
            "#app_launcher_container { background-color: #131212; border-top: 1px solid #424242; border-bottom: 1px solid #424242}"
        )
        layout = QVBoxLayout(container_widget)  # Use QVBoxLayout to stack grid and line edit
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Grid layout for apps
        self.grid_layout = QGridLayout()
        layout.addLayout(self.grid_layout)

        # Container for the line edit and clear button
        args_layout = QHBoxLayout()

        # Line edit for additional arguments
        self.additional_args_line_edit = QLineEdit()
        self.additional_args_line_edit.setPlaceholderText("Additional arguments...")
        fxguiutils.set_formatted_tooltip(
            self.additional_args_line_edit,
            "Additional Arguments",
            "Additional arguments to pass to the executable, e.g. <code>--flag value -h</code>.",
        )

        args_layout.addWidget(self.additional_args_line_edit)

        # Clear button for the line edit
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.additional_args_line_edit.clear)
        args_layout.addWidget(clear_button)
        layout.addLayout(args_layout)

        # Add the container widget to the tray menu
        self.list_apps_action = QWidgetAction(self.tray_menu)
        self.list_apps_action.setDefaultWidget(container_widget)
        self.tray_menu.insertAction(self.open_project_browser_action, self.list_apps_action)

        # Load apps
        self._load_and_display_apps(project_root, project_name)

    # ! Keep `project_name` argument for signal
    def _load_and_display_apps(self, project_root: str = None, project_name: str = None) -> None:
        """Loads the apps from the `apps.yaml` file and displays them in the
        grid layout.

        Args:
            project_root (str): The root path of the current project.
            project_name (str): The name of the current project.
        """

        # Clear existing widgets from the grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            self.grid_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

        # Load apps from YAML file
        project_info = fxcore.get_project()
        project_root = project_info.get("FXQUINOX_PROJECT_ROOT", None)
        apps_config_path = Path(project_root) / ".pipeline" / "project_config" / "apps.yaml"
        if not apps_config_path.exists():
            return
        apps_config = yaml.safe_load(apps_config_path.read_text())

        # Parse the `apps.yaml` file and add buttons for each app found
        row, col = 0, 0
        button_size = QSize(64, 64)

        for app_info in apps_config["apps"]:
            for app, details in app_info.items():
                version = details.get("version", {})
                version_major = version.get("major", 0)
                version_minor = version.get("minor", 0)
                version_patch = version.get("patch", 0)
                executable = (
                    details.get("executable", "")
                    .replace("$VERSION_MAJOR$", str(version_major))
                    .replace("$VERSION_MINOR$", str(version_minor))
                    .replace("$VERSION_PATCH$", str(version_patch))
                )
                commands = details.get("commands", [])
                icon_file = details.get("icon", "").replace("$FXQUINOX_ROOT$", fxenvironment.FXQUINOX_ROOT)

                # Create the button
                button = QPushButton()
                button.setIcon(QIcon(str(icon_file)))
                button.setIconSize(QSize(48, 48))
                button.setFixedSize(button_size)
                button.clicked.connect(lambda exe=executable, cmds=commands: self._launch_executable(exe, cmds))
                # Tooltip
                version_string = (
                    (
                        f"<b>Version</b>: {version_major if version_major else ''}"
                        f"{f'.{version_minor}' if version_minor else ''}"
                        f"{f'.{version_patch}' if version_patch else ''}<br><br>"
                    )
                    if version_major or version_minor or version_patch
                    else "<b>Version</b>: None<br><br>"
                )
                tooltip = (
                    f"{version_string}"
                    f"<b>Executable</b>: {executable if executable else None}<br><br>"
                    f"<b>Commands</b>: <code>{commands if commands else None}</code>"
                )
                fxguiutils.set_formatted_tooltip(button, app.capitalize(), tooltip)
                # Add the button to the grid layout
                self.grid_layout.addWidget(button, row, col)
                col += 1
                if col >= 4:
                    row += 1
                    col = 0

    def _launch_executable(self, executable: str, commands: list = None) -> None:
        """Launches the given executable, with optional commands.

        Args:
            executable (str): The path to the executable to launch.
            commands (list): The list of commands to pass to the executable.
        """

        additional_args = self.additional_args_line_edit.text().strip().split()
        if commands is None:
            commands = additional_args
        else:
            commands.extend(additional_args)

        runner_thread = FXExecutableRunnerThread(executable, commands)
        self.runner_threads.append(runner_thread)
        # Delete thread on completion
        runner_thread.finished.connect(lambda rt=runner_thread: self._on_thread_finished(rt))
        runner_thread.start()

    def _on_thread_finished(self, thread: FXExecutableRunnerThread) -> None:
        """Slot to handle thread finished signal. Attempt to remove the thread
        from the tracking list.

        Args:
            thread (FXExecutableRunnerThread): The thread that has finished.
        """

        thread.wait()  # Optional: Wait for the thread to fully finish if needed
        if thread in self.runner_threads:
            self.runner_threads.remove(thread)
        else:
            _logger.debug(f"Thread not found in list: '{thread}'")
        _logger.debug(f"Thread finished: '{thread}'")

    def _update_label(self, project_root: str = None, project_name: str = None) -> None:
        """Updates the label text with the current project name."""

        self.label.setText(project_name or "No project set")
        self._set_label_style(project_root, project_name)

    # ! Keep `project_root` argument for signal
    def _set_label_style(self, project_root: str = None, project_name: str = None) -> None:
        """Sets the label stylesheet based on the current project status.

        Args:
            project_root (str): The root path of the current project.
            project_name (str): The name of the current project.
        """

        if project_name:
            color = self.colors["feedback"]["success"]["light"]
        else:
            color = self.colors["feedback"]["warning"]["light"]
        self.label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12pt;")

    # ! Keep `project_root` argument for signal
    def _toggle_action_state(self, project_root: str = None, project_name: str = None) -> None:
        """Toggles the state of the actions based on the project status.

        Args:
            project_root (str): The root path of the current project.
            project_name (str): The name of the current project.
        """

        if project_name:
            self.open_project_browser_action.setEnabled(True)
            self.open_project_directory_action.setEnabled(True)
            self.list_apps_action.setEnabled(True)
        else:
            self.open_project_browser_action.setEnabled(False)
            self.open_project_directory_action.setEnabled(False)
            self.list_apps_action.setEnabled(False)

    def closeEvent(self, _) -> None:
        """Overrides the close event to handle the system tray close event."""

        _logger.info(f"Closed")
        self.setParent(None)
        fxutils.remove_lock(Path(fxenvironment.FXQUINOX_TEMP) / "launcher.lock")
        fxwidgets.FXApplication.instance().quit()
        QApplication.instance().quit()
