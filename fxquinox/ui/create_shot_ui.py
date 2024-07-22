# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'create_shot.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialogButtonBox,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QWidget)

class Ui_FXCreateShot(object):
    def setupUi(self, FXCreateShot):
        if not FXCreateShot.objectName():
            FXCreateShot.setObjectName(u"FXCreateShot")
        FXCreateShot.resize(743, 552)
        self.gridLayout = QGridLayout(FXCreateShot)
        self.gridLayout.setObjectName(u"gridLayout")
        self.line = QFrame(FXCreateShot)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 2, 0, 1, 3)

        self.combo_box_sequence = QComboBox(FXCreateShot)
        self.combo_box_sequence.setObjectName(u"combo_box_sequence")
        self.combo_box_sequence.setEditable(True)

        self.gridLayout.addWidget(self.combo_box_sequence, 0, 1, 1, 2)

        self.label_icon_sequence = QLabel(FXCreateShot)
        self.label_icon_sequence.setObjectName(u"label_icon_sequence")
        self.label_icon_sequence.setMaximumSize(QSize(18, 18))

        self.gridLayout.addWidget(self.label_icon_sequence, 0, 0, 1, 1)

        self.line_edit_shot = QLineEdit(FXCreateShot)
        self.line_edit_shot.setObjectName(u"line_edit_shot")

        self.gridLayout.addWidget(self.line_edit_shot, 1, 1, 1, 2)

        self.label_icon_shot = QLabel(FXCreateShot)
        self.label_icon_shot.setObjectName(u"label_icon_shot")
        self.label_icon_shot.setMaximumSize(QSize(18, 18))

        self.gridLayout.addWidget(self.label_icon_shot, 1, 0, 1, 1)

        self.button_box = QDialogButtonBox(FXCreateShot)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok|QDialogButtonBox.Reset)

        self.gridLayout.addWidget(self.button_box, 7, 0, 1, 3)

        self.label_icon_frame_range = QLabel(FXCreateShot)
        self.label_icon_frame_range.setObjectName(u"label_icon_frame_range")
        self.label_icon_frame_range.setMaximumSize(QSize(18, 18))

        self.gridLayout.addWidget(self.label_icon_frame_range, 3, 0, 1, 1)

        self.group_box_metadata = QGroupBox(FXCreateShot)
        self.group_box_metadata.setObjectName(u"group_box_metadata")
        self.gridLayout_2 = QGridLayout(self.group_box_metadata)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.button_add_metadata = QPushButton(self.group_box_metadata)
        self.button_add_metadata.setObjectName(u"button_add_metadata")

        self.gridLayout_2.addWidget(self.button_add_metadata, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(524, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.frame_metadata = QFrame(self.group_box_metadata)
        self.frame_metadata.setObjectName(u"frame_metadata")
        self.frame_metadata.setFrameShape(QFrame.NoFrame)
        self.frame_metadata.setFrameShadow(QFrame.Plain)
        self.frame_metadata.setLineWidth(0)

        self.gridLayout_2.addWidget(self.frame_metadata, 1, 0, 1, 2)


        self.gridLayout.addWidget(self.group_box_metadata, 6, 0, 1, 3)

        self.frame = QFrame(FXCreateShot)
        self.frame.setObjectName(u"frame")
        self.frame.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Plain)
        self.frame.setLineWidth(0)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_icon_thumbnail = QLabel(self.frame)
        self.label_icon_thumbnail.setObjectName(u"label_icon_thumbnail")
        self.label_icon_thumbnail.setMaximumSize(QSize(18, 18))

        self.horizontalLayout.addWidget(self.label_icon_thumbnail)

        self.line_edit_thumbnail = QLineEdit(self.frame)
        self.line_edit_thumbnail.setObjectName(u"line_edit_thumbnail")

        self.horizontalLayout.addWidget(self.line_edit_thumbnail)

        self.button_pick_thumbnail = QPushButton(self.frame)
        self.button_pick_thumbnail.setObjectName(u"button_pick_thumbnail")

        self.horizontalLayout.addWidget(self.button_pick_thumbnail)

        self.button_discard_thumbnail = QPushButton(self.frame)
        self.button_discard_thumbnail.setObjectName(u"button_discard_thumbnail")

        self.horizontalLayout.addWidget(self.button_discard_thumbnail)


        self.gridLayout.addWidget(self.frame, 4, 0, 1, 3)

        self.spin_box_cut_in = QSpinBox(FXCreateShot)
        self.spin_box_cut_in.setObjectName(u"spin_box_cut_in")
        self.spin_box_cut_in.setMaximum(999999999)
        self.spin_box_cut_in.setValue(1001)

        self.gridLayout.addWidget(self.spin_box_cut_in, 3, 1, 1, 1)

        self.spin_box_cut_out = QSpinBox(FXCreateShot)
        self.spin_box_cut_out.setObjectName(u"spin_box_cut_out")
        self.spin_box_cut_out.setMaximum(999999999)
        self.spin_box_cut_out.setValue(1100)

        self.gridLayout.addWidget(self.spin_box_cut_out, 3, 2, 1, 1)

        self.line_2 = QFrame(FXCreateShot)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_2, 5, 0, 1, 3)


        self.retranslateUi(FXCreateShot)

        QMetaObject.connectSlotsByName(FXCreateShot)
    # setupUi

    def retranslateUi(self, FXCreateShot):
        FXCreateShot.setWindowTitle(QCoreApplication.translate("FXCreateShot", u"Form", None))
#if QT_CONFIG(tooltip)
        self.combo_box_sequence.setToolTip(QCoreApplication.translate("FXCreateShot", u"<b>Sequence</b><hr>The parent sequence. If not existing, will be created.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.combo_box_sequence.setStatusTip(QCoreApplication.translate("FXCreateShot", u"The parent sequence. If not existing, will be created", None))
#endif // QT_CONFIG(statustip)
        self.label_icon_sequence.setText(QCoreApplication.translate("FXCreateShot", u"Icon", None))
#if QT_CONFIG(tooltip)
        self.line_edit_shot.setToolTip(QCoreApplication.translate("FXCreateShot", u"<b>Shot</b><hr>The shot to create.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.line_edit_shot.setStatusTip(QCoreApplication.translate("FXCreateShot", u"The shot to create", None))
#endif // QT_CONFIG(statustip)
        self.line_edit_shot.setPlaceholderText(QCoreApplication.translate("FXCreateShot", u"Shot...", None))
        self.label_icon_shot.setText(QCoreApplication.translate("FXCreateShot", u"Icon", None))
        self.label_icon_frame_range.setText(QCoreApplication.translate("FXCreateShot", u"Icon", None))
        self.group_box_metadata.setTitle(QCoreApplication.translate("FXCreateShot", u"Metadata", None))
#if QT_CONFIG(tooltip)
        self.button_add_metadata.setToolTip(QCoreApplication.translate("FXCreateShot", u"<b>Metadata</b><hr>Add custom metadata to the shot.", None))
#endif // QT_CONFIG(tooltip)
        self.button_add_metadata.setText("")
        self.label_icon_thumbnail.setText(QCoreApplication.translate("FXCreateShot", u"Icon", None))
#if QT_CONFIG(tooltip)
        self.line_edit_thumbnail.setToolTip(QCoreApplication.translate("FXCreateShot", u"<b>Thumbnail</b><hr>Choose the thumbnail image that will be displayed.", None))
#endif // QT_CONFIG(tooltip)
        self.line_edit_thumbnail.setPlaceholderText(QCoreApplication.translate("FXCreateShot", u"Thumbnail...", None))
        self.button_pick_thumbnail.setText(QCoreApplication.translate("FXCreateShot", u"Pick", None))
        self.button_discard_thumbnail.setText(QCoreApplication.translate("FXCreateShot", u"Discard", None))
#if QT_CONFIG(tooltip)
        self.spin_box_cut_in.setToolTip(QCoreApplication.translate("FXCreateShot", u"<b>Cut In</b><hr>The frame cut in of the shot.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.spin_box_cut_out.setToolTip(QCoreApplication.translate("FXCreateShot", u"<b>Cut Out</b><hr>The frame cut out of the shot.", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

