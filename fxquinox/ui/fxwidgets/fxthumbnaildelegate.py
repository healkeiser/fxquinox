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
    # The `show_thumbnail` flag should be stored in the `Qt.UserRole + 1` as bool
    # The thumbnail path should be stored in the `Qt.UserRole + 2` as str

    def sizeHint(
        self, option: QStyleOptionViewItem, index: QModelIndex
    ) -> QSize:
        """Return the size hint for the item at the given index.

        Args:
            option (QStyleOptionViewItem): The style options for the item.
            index (QModelIndex): The model index of the item.

        Returns:
            QSize: The size hint for the item.
        """
        show_thumbnail = index.data(Qt.UserRole + 1)
        if (
            show_thumbnail is None or show_thumbnail
        ):  # Show thumbnail by default
            original_size = super().sizeHint(option, index)
            return QSize(
                original_size.width(), 50
            )  # Increased item height for thumbnails
        else:
            original_size = super().sizeHint(option, index)
            return QSize(
                original_size.width(), 20
            )  # Reduced item height without thumbnails

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> None:
        """Paint the item at the given index with the given painter.

        Args:
            painter (QPainter): The painter to use for drawing.
            option (QStyleOptionViewItem): The style options for the item.
            index (QModelIndex): The model index of the item.
        """

        # Draw the selection background for the entire item first
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        else:
            pass
            # # Draw alternating row colors
            # if index.row() % 2 == 0:
            #     painter.fillRect(option.rect, option.palette.base())
            # else:
            #     painter.fillRect(option.rect, option.palette.alternateBase())

        # Initialize variables for thumbnail dimensions and offsets
        x_offset = 5
        y_offset = 5
        thumbnail_width_with_padding = 0

        # Check if it's the first column and the thumbnail should be shown
        if index.column() == 0:
            show_thumbnail = index.data(Qt.UserRole + 1)
            if (
                show_thumbnail is None or show_thumbnail
            ):  # Show thumbnail by default
                thumbnail_path = index.data(Qt.UserRole + 2)
                if not thumbnail_path:
                    thumbnail_path = str(
                        Path(fxenvironment._FQUINOX_IMAGES)
                        / "missing_image.png"
                    )
                thumbnail = QPixmap(thumbnail_path)

                item_height = (
                    option.rect.height() - 10
                )  # 5 pixels space on top and bottom
                thumbnail = thumbnail.scaledToHeight(
                    item_height - 2, Qt.SmoothTransformation
                )

                bordered_thumbnail = QPixmap(thumbnail.size() + QSize(2, 2))
                bordered_thumbnail.fill(Qt.transparent)

                painter_with_border = QPainter(bordered_thumbnail)
                painter_with_border.setRenderHint(QPainter.Antialiasing)
                painter_with_border.setPen(QPen(Qt.white, 1))
                painter_with_border.setBrush(QBrush(thumbnail))
                radius = 2
                painter_with_border.drawRoundedRect(
                    bordered_thumbnail.rect().marginsRemoved(
                        QMargins(1, 1, 1, 1)
                    ),
                    radius,
                    radius,
                )
                painter_with_border.end()

                # Calculate the position to draw the thumbnail
                y = option.rect.top() + y_offset

                # Draw the thumbnail
                painter.drawPixmap(
                    option.rect.left() + x_offset, y, bordered_thumbnail
                )

                # Update the width for the thumbnail with padding
                thumbnail_width_with_padding = (
                    bordered_thumbnail.width() + x_offset * 2
                )

        # Adjust the rectangle for drawing the text and icon to not overlap the thumbnail
        text_icon_rect = QRect(
            option.rect.left() + thumbnail_width_with_padding,
            option.rect.top(),
            option.rect.width() - thumbnail_width_with_padding,
            option.rect.height(),
        )

        # Create a new option for drawing the text and icon
        new_option = QStyleOptionViewItem(option)
        new_option.rect = text_icon_rect

        # Draw the icon and text with the modified option
        super().paint(painter, new_option, index)
