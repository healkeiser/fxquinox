# Built-in
import sys
import subprocess

# Third-party
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *

# Internal
from fxquinox import fxlog


# Log
_logger = fxlog.get_logger("fxexecutablerunnerthread")
_logger.setLevel(fxlog.DEBUG)


class FXExecutableRunnerThread(QThread):
    """A QThread subclass to run an executable in a separate thread.

    Args:
        executable (str): The path to the executable to run.
        commands (list): A list of arguments to pass to the executable.
        parent (QObject): The parent object of the thread.

    Attributes:
        executable (str): The path to the executable to run.
        commands (list): A list of arguments to pass to the executable.
        finished (Signal): A signal to emit upon completion.
    """

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
