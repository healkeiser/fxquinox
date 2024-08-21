# Built-in
import os
from pathlib import Path
from PIL import Image
import shutil
import sys

if sys.version_info < (3, 11):
    os.environ["QT_API"] = "pyside2"
else:
    os.environ["QT_API"] = "pyside6"

# Third-party
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *
import mss

# Internal
from fxquinox import fxenvironment, fxlog


# Log
_logger = fxlog.get_logger("fxscreencapturewindow")
_logger.setLevel(fxlog.DEBUG)


class FXScreenCaptureWindow(QMainWindow):
    """A window for capturing a screen region.

    Args:
        entity_name (str): The name of the entity to capture the thumbnail for.
        entity_dir (str): The directory of the entity to capture the
            thumbnail for.

    Attributes:
        rubber_band (QRubberBand): The rubber band for selecting the screen
            region.
        origin (QPoint): The origin point of the screen region selection.
        workfile (str): The name of the workfile to capture the thumbnail for.
        workfile_dir (str): The directory of the workfile to capture the
            thumbnail for.
    """

    selection_complete = Signal(str)

    def __init__(
        self,
        parent: QWidget = None,
        entity_name: str = None,
        entity_dir: str = None,
        capture_thumbnail: bool = True,
    ):
        super().__init__(parent)

        # Attributes
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.entity_name: str = entity_name
        self.entity_dir: str = entity_dir
        self.captured_image_path = ""
        self.capture_thumbnail: bool = capture_thumbnail

        # Methods
        self.setWindowTitle("Screen Capture")
        # self.start_capture()

    def start_capture(self):
        screen = QApplication.primaryScreen()
        rectangle = screen.geometry()
        self.setGeometry(rectangle)
        self.showFullScreen()
        self.setWindowOpacity(0.3)
        self.setCursor(Qt.CrossCursor)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen
        )
        # self.show()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.origin = event.pos()
        self.rubber_band.setGeometry(QRect(self.origin, QSize()))
        self.rubber_band.show()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.rubber_band.setGeometry(
            QRect(self.origin, event.pos()).normalized()
        )

    def mouseReleaseEvent(self, _) -> None:
        self.rubber_band.hide()
        rectangle = self.rubber_band.geometry()
        self.hide()  # Hide the window before capturing the screen
        self.capture_screen_region(
            rectangle.left(),
            rectangle.top(),
            rectangle.width(),
            rectangle.height(),
            str(Path(fxenvironment.FXQUINOX_TEMP) / "thumbnail.jpg"),
        )
        self.close()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()

    def capture_screen_region(
        self, left: int, top: int, width: int, height: int, temp_save_path: str
    ) -> None:
        """Capture the screen region and save it to the given path.

        Args:
            left (int): The left coordinate of the screen region.
            top (int): The top coordinate of the screen region.
            width (int): The width of the screen region.
            height (int): The height of the screen region.
            temp_save_path (str): The path to temporarily save the captured image.
        """

        with mss.mss() as sct:
            monitor = {
                "left": left,
                "top": top,
                "width": width,
                "height": height,
            }
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            img.save(temp_save_path)

            if self.entity_name and self.entity_dir and self.capture_thumbnail:
                self.resize_image(self.entity_name, self.entity_dir)
                Path(temp_save_path).unlink()

    def resize_image(self, entity_name: str, entity_dir: str) -> None:
        old_thumbnail_path = str(
            Path(fxenvironment.FXQUINOX_TEMP) / "thumbnail.jpg"
        )
        thumbnail_name = f"{entity_name}.jpg"
        thumbnail_dir = Path(entity_dir) / ".thumbnails"
        thumbnail_dir.mkdir(parents=True, exist_ok=True)
        new_thumbnail_path = thumbnail_dir / thumbnail_name
        shutil.copy(old_thumbnail_path, new_thumbnail_path)

        # Resize and convert the copied image to JPG
        target_width, target_height = 480, 270
        with Image.open(new_thumbnail_path) as img:
            # Calculate the scaling factor to ensure at least one side matches
            # the target size
            scaling_factor = max(
                target_width / img.width, target_height / img.height
            )

            # Resize the image with the scaling factor
            new_size = (
                int(img.width * scaling_factor),
                int(img.height * scaling_factor),
            )
            img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Calculate the cropping area
            left = (img.width - target_width) / 2
            top = (img.height - target_height) / 2
            right = (img.width + target_width) / 2
            bottom = (img.height + target_height) / 2

            # Crop the image to the target size
            img = img.crop((left, top, right, bottom))

            # Convert to RGB and save
            img.convert("RGB").save(new_thumbnail_path, "JPEG")

        # Set the captured image path, emit the signal
        self.captured_image_path = Path(new_thumbnail_path).as_posix()
        self.emit_selection_complete(self.captured_image_path)

    def emit_selection_complete(self, path: str):
        """Emit the selection_complete signal with the given path.

        Args:
            path (str): The path to the captured image.
        """

        self.captured_image_path = path
        self.selection_complete.emit(path)
        self.close()

    def get_captured_image_path(self):
        return self.captured_image_path

    def _exec(self):
        self.start_capture()
        self.show()
