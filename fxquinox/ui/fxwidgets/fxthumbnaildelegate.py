# Built-in
from pathlib import Path

# Third-partys
from qtpy.QtWidgets import *
from qtpy.QtUiTools import *
from qtpy.QtCore import *
from qtpy.QtGui import *

# Internal
from fxquinox import fxenvironment, fxlog

# Log
_logger = fxlog.get_logger("fxthumbnaildelegate")
_logger.setLevel(fxlog.DEBUG)


class FXThumbnailItemDelegate(QStyledItemDelegate):
    # ! The `show_thumbnail` flag should be stored in the `Qt.UserRole + 1` as bool
    # ! The thumbnail path should be stored in the `Qt.UserRole + 2` as str

    def sizeHint(self, option, index):
        # Check if the thumbnail should be shown
        show_thumbnail = index.data(Qt.UserRole + 1)
        if show_thumbnail is None or show_thumbnail:  # Show thumbnail by default
            # Increase the height of the items for thumbnails
            original_size = super().sizeHint(option, index)
            return QSize(original_size.width(), 50)  # Increased item height for thumbnails
        else:
            # Return a smaller height if the thumbnail is disabled
            original_size = super().sizeHint(option, index)
            return QSize(original_size.width(), 20)  # Reduced item height without thumbnails

    def paint(self, painter, option, index):
        # Fill the entire item's background first
        background_color = (
            option.palette.window() if not (option.state & QStyle.State_Selected) else option.palette.highlight()
        )
        painter.fillRect(option.rect, background_color)
        if index.column() == 0:  # Check if it's the first column
            # Check if the thumbnail should be shown
            show_thumbnail = index.data(Qt.UserRole + 1)
            if show_thumbnail is None or show_thumbnail:  # Show thumbnail by default
                # Load the thumbnail
                thumbnail_path = index.data(Qt.UserRole + 2)
                if thumbnail_path:
                    thumbnail = QPixmap(thumbnail_path)
                else:
                    # Fallback path if no thumbnail path is set
                    thumbnail_path = Path(fxenvironment._FQUINOX_IMAGES) / "missing_image.png"
                    thumbnail = QPixmap(thumbnail_path.resolve().as_posix())

                # Adjust the target height for scaling the thumbnail, subtracting 10 pixels for top and bottom spaces
                item_height = option.rect.height() - 10  # 5 pixels space on top and bottom
                thumbnail = thumbnail.scaledToHeight(item_height - 2, Qt.SmoothTransformation)  # Subtract border width

                # Create a new QPixmap for the border and rounded corners
                bordered_thumbnail = QPixmap(thumbnail.size() + QSize(2, 2))  # Add space for the border
                bordered_thumbnail.fill(Qt.transparent)  # Fill with transparent background

                # Use QPainter to draw the border and image with rounded corners
                painter_with_border = QPainter(bordered_thumbnail)
                painter_with_border.setRenderHint(QPainter.Antialiasing)
                painter_with_border.setPen(QPen(Qt.white, 1))  # White pen for the border
                painter_with_border.setBrush(QBrush(thumbnail))  # Use the thumbnail as the brush
                radius = 2  # Adjust radius
                painter_with_border.drawRoundedRect(
                    bordered_thumbnail.rect().marginsRemoved(QMargins(1, 1, 1, 1)), radius, radius
                )

                painter_with_border.end()  # Finish drawing

                # Adjust the y-coordinate to add a 5-pixel offset from the top
                x_offset = 5  # Offset from the left border of the item
                y_offset = 5  # Pixels space on top
                y = option.rect.top() + y_offset  # Align to the top of the item with a 5-pixel offset

                painter.drawPixmap(option.rect.left() + x_offset, y, bordered_thumbnail)

                # Adjust the option.rect for the icon and text to be on the right of the thumbnail
                thumbnail_width_with_padding = bordered_thumbnail.width() + x_offset * 2
            else:
                # If not showing thumbnail, adjust padding as if there's no thumbnail
                thumbnail_width_with_padding = 0

            new_option = QStyleOptionViewItem(option)
            new_option.rect = QRect(
                option.rect.left() + thumbnail_width_with_padding,
                option.rect.top(),
                option.rect.width() - thumbnail_width_with_padding,
                option.rect.height(),
            )

            # Call the base class paint method with the adjusted rect
            super().paint(painter, new_option, index)
        else:
            # For other columns, use the default painting
            super().paint(painter, option, index)
