# Built-in
from pathlib import Path
from functools import partial
import sys
import subprocess
import textwrap
from typing import Optional, Dict

# Third-party
from fxgui import fxwidgets, fxicons, fxstyle, fxutils as fxguiutils
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *
import yaml

# Internal
from fxquinox import fxenvironment, fxlog, fxutils, fxcore
from fxquinox.ui.fxwidgets import fxprojectbrowser
from fxquinox.ui.fxwidgets.fxdialog import FXDialog


# Log
_logger = fxlog.get_logger("fxlauncher")
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
            call = [self.executable] + (self.commands if self.commands else [])
        else:
            if self.commands:
                call = self.commands
            else:
                _logger.error("No executable or commands provided to run")
                self.finished.emit()
                return

        if sys.platform == "win32":
            cmd = ["cmd.exe", "/c"] + call
            _logger.debug(f"cmd: {cmd}")
            subprocess.Popen(cmd, shell=True)
        else:
            subprocess.Popen(call, shell=True)

        _logger.debug(f"Call: {call}")
        self.finished.emit()


class FXLauncherSystemTray(fxwidgets.FXSystemTray):
    """The Fxquinox main launcher UI class.

    Args:
        parent (QWidget): The parent widget.
        icon (QIcon): The icon to display in the system tray.
        project (str): The current project name.

    Attributes:
        project (str): The current project name.
        colors (dict): The color dictionary.
        runner_threads (list): A list of runner threads.

    Signals:
        project_changed (dict): The signal emitted when the project is
            changed.

    Note:
        This class inherits from `FXSystemTray` which is a custom system tray
        class that inherits from `QSystemTrayIcon`.
    """

    project_changed = Signal(dict)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        icon: Optional[str] = None,
        project: Optional[str] = None,
        #
        project_info: Optional[Dict] = None,
    ):
        super().__init__(parent, icon)

        # Attributes
        self.project = project
        self.project_info = project_info
        self.colors = fxstyle.load_colors_from_jsonc()
        self.runner_threads = []

        _logger.debug(f"Launcher project: '{self.project}'")

        # Methods
        self._get_project()
        self.__create_actions()
        self.__handle_connections()
        self._create_label()
        self._create_app_launcher()
        self._update_label()
        self._toggle_action_state()

    def _get_project(self) -> None:
        """Gets the project information from the environment variables or the
        configuration file.
        """

        if all(not value for value in self.project_info.values()):
            self.project_info = fxcore.get_project()
        self._project_root = self.project_info.get("FXQUINOX_PROJECT_ROOT", None)
        self._project_name = self.project_info.get("FXQUINOX_PROJECT_NAME", None)
        self._project_assets_path = self.project_info.get("FXQUINOX_PROJECT_ASSETS_PATH", None)
        self._project_shots_path = self.project_info.get("FXQUINOX_PROJECT_SHOTS_PATH", None)

    def __handle_connections(self) -> None:
        """Connects the signals to the slots.

        Note:
            Using `__` in function name to avoid name clashes with the parent
            class.
        """

        self.project_changed.connect(self._get_project)
        self.project_changed.connect(self._update_label)
        self.project_changed.connect(self._toggle_action_state)
        self.project_changed.connect(self._load_and_display_apps)
        self.project_changed.connect(lambda: _logger.debug(f"Project changed: '{self.project}'"))

    def __create_actions(self) -> None:
        """Creates the actions for the system tray.

        Note:
            Using `__` in function name to avoid name clashes with the parent
            class.
        """

        self.create_project_action = fxguiutils.create_action(
            self.tray_menu,
            "Create Project...",
            fxicons.get_icon("movie_filter"),
            None,
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
            fxprojectbrowser.run_project_browser,
        )

        self.open_project_directory_action = fxguiutils.create_action(
            self.tray_menu,
            "Open Project Directory...",
            fxicons.get_icon("open_in_new"),
            self._open_project_directory,
        )

        # Fxquinox menu
        self.fxquinox_menu = QMenu("Fxquinox", self.tray_menu)
        self.fxquinox_menu.setIcon(QIcon(str(Path(fxenvironment._FQUINOX_IMAGES) / "fxquinox_logo_light.svg")))

        self.open_fxquinox_appdata = fxguiutils.create_action(
            self.fxquinox_menu,
            "Open Application Data Directory...",
            fxicons.get_icon("open_in_new"),
            lambda: fxutils.open_directory(fxenvironment.FXQUINOX_APPDATA),
        )

        self.open_fxquinox_temp = fxguiutils.create_action(
            self.fxquinox_menu,
            "Open Temp Directory...",
            fxicons.get_icon("open_in_new"),
            lambda: fxutils.open_directory(fxenvironment.FXQUINOX_TEMP),
        )

        # Log level menu
        self.log_menu = QMenu("Log Level", self.tray_menu)
        self.log_menu.setIcon(fxicons.get_icon("settings"))

        # Create an action group for mutually exclusive actions
        log_level_group = QActionGroup(self.log_menu)
        log_level_group.setExclusive(True)

        # Define log levels
        log_levels = {
            "Debug": fxlog.DEBUG,
            "Info": fxlog.INFO,
            "Warning": fxlog.WARNING,
            "Error": fxlog.ERROR,
            "Critical": fxlog.CRITICAL,
        }

        # Create and add actions for each log level
        for level_name, level in log_levels.items():
            action = QAction(level_name, self.log_menu, checkable=True)
            action.triggered.connect(partial(self._set_log_level, level=level))
            log_level_group.addAction(action)
            self.log_menu.addAction(action)

        # Set a default log level
        default_action = log_level_group.actions()[0]  # Setting `Debug` as default
        default_action.setChecked(True)
        self._set_log_level(log_levels[default_action.text()])

        self.tray_menu.insertAction(self.quit_action, self.open_project_directory_action)
        self.tray_menu.insertAction(self.open_project_directory_action, self.open_project_browser_action)
        self.tray_menu.insertAction(self.open_project_browser_action, self.set_project_action)

        self.tray_menu.insertMenu(self.quit_action, self.fxquinox_menu)
        self.fxquinox_menu.addAction(self.open_fxquinox_appdata)
        self.fxquinox_menu.addAction(self.open_fxquinox_temp)
        self.tray_menu.insertMenu(self.quit_action, self.log_menu)

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

    def _create_app_launcher(self) -> None:
        """Creates the application launcher as a grid and adds a QLineEdit for
        additional arguments.
        """

        # Main container widget
        container_widget = QWidget()
        container_widget.setObjectName("app_launcher_container")
        container_widget.setStyleSheet(
            "#app_launcher_container { background-color: #131212; border-top: 1px solid #424242; border-bottom: 1px solid #424242}"
        )
        container_widget.setFixedSize(330, 300)

        main_layout = QVBoxLayout(container_widget)  # Main layout for everything
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Scroll Area Setup
        scroll_area = QScrollArea()
        scroll_area.setContentsMargins(0, 0, 0, 0)
        scroll_area.setObjectName("scroll_app_launcher_container")
        scroll_area.setStyleSheet(
            "#scroll_app_launcher_container { border: 0px solid transparent; } #scroll_app_launcher_container > QWidget > QWidget { background-color: transparent; }"
        )
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_widget = QWidget()  # This widget will be inside the scroll area
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(scroll_widget)

        # Grid layout for apps inside the scroll area
        self.grid_layout = QGridLayout()
        scroll_layout.addLayout(self.grid_layout)

        # Container for the line edit and clear button, placed outside the scroll area
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

        # Add the scroll area and args layout to the main layout
        main_layout.addWidget(scroll_area)
        main_layout.addLayout(args_layout)

        # Add the container widget to the tray menu
        self.list_apps_action = QWidgetAction(self.tray_menu)
        self.list_apps_action.setDefaultWidget(container_widget)
        self.tray_menu.insertAction(self.open_project_browser_action, self.list_apps_action)

        # Load apps
        self._load_and_display_apps()

    def _load_and_display_apps(self) -> None:
        """Loads the apps from the `apps.yaml` file and displays them in the
        grid layout.

        Args:
            project_root (str): The root path of the current project.
            project_name (str): The name of the current project.
        """

        _logger.debug(f"Loading apps for project: '{self._project_name}'")

        # Clear existing widgets from the grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            self.grid_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

        # Load apps from YAML file
        project_info = self.project_info
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
                # button.clicked.connect(lambda exe=executable, cmds=commands: self._launch_executable(exe, cmds))
                button.clicked.connect(partial(self._launch_executable, executable, commands))

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

                _logger.debug(f"Added app: '{app}'")

                # Aloow only 4 apps per row
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

        _logger.info(f"Launching executable: '{executable}' with commands: '{commands}'")

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

    def _update_label(self) -> None:
        """Updates the label text with the current project name."""

        self.label.setText(self._project_name or "No project set")
        self._set_label_style()

    def _set_label_style(self) -> None:
        """Sets the label stylesheet based on the current project status."""

        if self._project_name:
            color = self.colors["feedback"]["success"]["light"]
        else:
            color = self.colors["feedback"]["warning"]["light"]
        self.label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12pt;")

    def _toggle_action_state(self) -> None:
        """Toggles the state of the actions based on the project status.

        Args:
            project_root (str): The root path of the current project.
            project_name (str): The name of the current project.
        """

        if self._project_name:
            self.open_project_browser_action.setEnabled(True)
            self.open_project_directory_action.setEnabled(True)
            self.list_apps_action.setEnabled(True)
        else:
            self.open_project_browser_action.setEnabled(False)
            self.open_project_directory_action.setEnabled(False)
            self.list_apps_action.setEnabled(False)

    def _open_project_directory(self) -> None:
        """Opens the project directory in the system file manager."""

        project_root = self.project_info.get("FXQUINOX_PROJECT_ROOT", None)
        if project_root:
            fxutils.open_directory(project_root)
        else:
            _logger.warning("No project set")

    def _set_log_level(self, level: int = fxlog.DEBUG) -> None:
        """Sets the log level for all loggers created by the `FXFormatter`.

        Args:
            level (int): The logging level to set.
        """

        fxlog.set_log_level(level)

    def closeEvent(self, _) -> None:
        """Overrides the close event to handle the system tray close event."""

        _logger.info(f"Closed")
        self.setParent(None)
        fxutils.remove_lock_file(Path(fxenvironment.FXQUINOX_TEMP) / "launcher.lock")
        fxwidgets.FXApplication.instance().quit()
        QApplication.instance().quit()


def run_launcher(
    parent: QWidget = None, quit_on_last_window_closed: bool = True, show_splashscreen: bool = False
) -> None:
    """Runs the launcher UI.

    Args:
        quit_on_last_window_closed (bool): Whether to quit the application when
            the last window is closed. Defaults to `True`.
        show_splashscreen (bool): Whether to show the splash screen.
            Defaults to `False`.
    """

    # Application
    if not parent:
        app = fxwidgets.FXApplication().instance()
        app.setQuitOnLastWindowClosed(quit_on_last_window_closed)

    # Check for an existing lock file
    lock_file = Path(fxenvironment.FXQUINOX_TEMP) / "launcher.lock"
    if not fxutils.check_and_create_lock_file(lock_file):
        warning = QMessageBox(parent)
        warning.setWindowIcon(QIcon(str(Path(fxenvironment._FQUINOX_IMAGES) / "fxquinox_logo_background_dark.svg")))
        warning.setWindowTitle(f"Launcher Already Running")
        warning.setText(
            f"The launcher is already running.<br><br>" f"Close the existing launcher before starting a new one."
        )
        warning.setIcon(QMessageBox.Warning)
        warning.exec_()
        _logger.warning("Launcher already running")
        return
    else:
        _logger.debug(f"Lock file created: {lock_file.as_posix()}")

    # Get the current project
    project_info = fxcore.get_project()
    project_root = project_info.get("FXQUINOX_PROJECT_ROOT", None)
    project_name = project_info.get("FXQUINOX_PROJECT_NAME", None)

    # If it doesn't exist but has been set in the environment file, error
    if project_root and not Path(project_root).exists():
        _logger.error(f"Project set in the environment file doesn't exist: '{project_root}'")
        confirmation = QMessageBox(parent)
        confirmation.setWindowIcon(
            QIcon(str(Path(fxenvironment._FQUINOX_IMAGES) / "fxquinox_logo_background_dark.svg"))
        )
        confirmation.setWindowTitle(f"Corrupted Project")
        confirmation.setText(
            f"Project set in the environment file doesn't exist: <code>{project_root}</code><br><br>"
            f"Fix the configuration file?"
        )
        confirmation.setIcon(QMessageBox.Critical)
        confirmation.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirmation.setDefaultButton(QMessageBox.Yes)
        confirmation_response = confirmation.exec_()
        if confirmation_response == QMessageBox.No:
            _logger.info(f"Environment file deletion cancelled")
            return

        _config = {
            "project": {"root": "", "name": "", "assets_path": "", "shots_path": ""},
        }
        fxutils.update_configuration_file("fxquinox.cfg", _config)
        _logger.info(f"Environment '{Path(fxenvironment.FXQUINOX_ENV_FILE).as_posix()}' file updated")

        # Refresh the current project reading the new configuration file
        project_info = fxcore.get_project(from_file=True)
        project_root = project_info.get("FXQUINOX_PROJECT_ROOT", None)
        project_name = project_info.get("FXQUINOX_PROJECT_NAME", None)

    # Icon and image paths
    images_path = Path(fxenvironment._FQUINOX_IMAGES)
    icon_path = Path(images_path / "fxquinox_logo_light.svg").resolve().as_posix()

    # Splashscreen
    if show_splashscreen:
        splash_image_path = Path(images_path / "splash.png").resolve().as_posix()
        information = textwrap.dedent(
            """\
        USD centric pipeline for feature animation and VFX projects. Made with love by Valentin Beaumont.

        This project is a very early work in progress and is not ready for production use.
        """
        )
        splashscreen = fxwidgets.FXSplashScreen(
            image_path=splash_image_path,
            icon=icon_path,
            title="Fxquinox",
            information=information,
            project=project_name or "No project set",
            version="0.0.1",
            company="fxquinox",
        )
        splashscreen.show()

        # ' Launcher
        splashscreen.showMessage("Communication with CG gods...")
        splashscreen.showMessage("Loading project...")
        temp_widget = _FXTempWidget(parent=None)
        splashscreen.showMessage("Starting launcher...")
        launcher = FXLauncherSystemTray(parent=None, icon=icon_path, project=project_name, project_info=project_info)
        splashscreen.finish(temp_widget)

    # No splashscreen
    else:
        launcher = FXLauncherSystemTray(parent=None, icon=icon_path, project=project_name, project_info=project_info)

    launcher.show()
    _logger.info("Started launcher")

    if not parent:
        app.exec_()


if __name__ == "__main__":
    run_launcher(parent=None, show_splashscreen=False)
