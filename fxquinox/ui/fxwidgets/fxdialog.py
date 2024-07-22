# Built-in
from pathlib import Path
from typing import Callable, Optional
from typing_extensions import Literal

# Third-party
from fxgui import fxwidgets, fxicons, fxstyle
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *

# Internal
from fxquinox import fxenvironment, fxlog


# Log
_logger = fxlog.get_logger("fxdialog")
_logger.setLevel(fxlog.DEBUG)

# Constants
INFO = "info"
WARNING = "warning"
ERROR = "error"
SUCCESS = "success"


class FXDialog(QDialog):
    def __init__(
        self,
        parent: QWidget = None,
        dialog_type: Literal["info", "warning", "error", "success"] = INFO,
        *args,
        **kwargs
    ):
        super().__init__(parent, *args, **kwargs)

        self.setWindowIcon(QIcon(str(Path(fxenvironment._FQUINOX_IMAGES) / "fxquinox_logo_background_dark.svg")))
        self.resize(400, 200)

        # Attributes
        self.colors_dict = fxstyle.load_colors_from_jsonc()
        self.icon_label = QLabel()
        self.message_label = QLabel("Message", alignment=Qt.AlignLeft)
        self.details_label = QTextEdit("Details", readOnly=True, visible=False)
        self.toggle_button = QPushButton(
            icon=fxicons.get_icon("keyboard_arrow_left"), fixedSize=QSize(24, 24), visible=False
        )
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.icon_spacing_widget = QWidget(fixedWidth=10)

        # Methods
        self._setup_layout()
        self._update_icon(dialog_type)
        self._handle_connections()

    def _setup_layout(self):
        message_layout = QHBoxLayout()
        message_layout.addWidget(self.icon_label)
        message_layout.addWidget(self.icon_spacing_widget)
        message_layout.addWidget(self.message_label)
        message_layout.addStretch()

        toggle_button_layout = QHBoxLayout()
        toggle_button_layout.addStretch()
        toggle_button_layout.addWidget(self.toggle_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(message_layout)
        main_layout.addLayout(toggle_button_layout)
        main_layout.addWidget(self.details_label)
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def _handle_connections(self):
        self.toggle_button.clicked.connect(self._toggle_details)
        self.button_box.accepted.connect(self.accept)

    def _update_icon(self, dialog_type: Literal["info", "warning", "error", "success"]):
        icon_color = self.colors_dict["feedback"][dialog_type]["light"]
        self.icon_label.setPixmap(fxicons.get_pixmap(dialog_type, color=icon_color))

    def _toggle_details(self):
        is_visible = not self.details_label.isVisible()
        self.details_label.setVisible(is_visible)
        self.toggle_button.setIcon(fxicons.get_icon("keyboard_arrow_down" if is_visible else "keyboard_arrow_left"))

    def add_button(
        self, text: str, role: QDialogButtonBox.ButtonRole, callback: Optional[Callable] = None
    ) -> QPushButton:
        """Add a button to the dialog.

        Args:
            text (str): The text to display on the button.
            role (QDialogButtonBox.ButtonRole): The role of the button.
            callback (Optional[Callable], optional): The callback to connect to
                the button. Defaults to `None`.

        Returns:
            QPushButton: The button that was added.
        """

        button = self.button_box.addButton(text, role)
        if callback:
            button.clicked.connect(callback)
        return button

    def set_message(self, message: str) -> None:
        """Sets the main message of the dialog.

        Args:
            message (str): The message text.
        """

        self.message_label.setText(message)

    def set_details(self, details: str) -> None:
        """Sets the detailed text of the dialog and makes the details
        section visible if not empty.

        Args:
            details (str): The details text.
        """

        self.details_label.setText(details)
        self.toggle_button.setVisible(bool(details))
        if details:
            self._toggle_details()

    def hide_icon(self):
        """Hide the icon in the dialog."""

        self.icon_label.setVisible(False)
        self.icon_spacing_widget.setVisible(False)

    def show_icon(self):
        """Show the icon in the dialog."""

        self.icon_label.setVisible(True)
        self.icon_spacing_widget.setVisible(True)


if __name__ == "__main__":
    app = fxwidgets.FXApplication.instance()
    dialog = FXDialog(dialog_type="warning")
    dialog.hide_icon()
    dialog.set_message("This is a message.")
    dialog.set_details("These are the details.")
    dialog.add_button("Cancel", QDialogButtonBox.RejectRole, dialog.reject)
    result = dialog.exec_()
    if result == QDialog.Accepted:
        print("Accepted")
    elif result == QDialog.Rejected:
        print("Rejected")
