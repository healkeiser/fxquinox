# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'save_workfile.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialogButtonBox,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(898, 464)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.group_box_current = QGroupBox(Form)
        self.group_box_current.setObjectName(u"group_box_current")
        self.verticalLayout_2 = QVBoxLayout(self.group_box_current)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame_workfile = QFrame(self.group_box_current)
        self.frame_workfile.setObjectName(u"frame_workfile")
        self.frame_workfile.setFrameShape(QFrame.NoFrame)
        self.frame_workfile.setFrameShadow(QFrame.Plain)
        self.frame_workfile.setLineWidth(0)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_workfile)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_icon_workfile = QLabel(self.frame_workfile)
        self.label_icon_workfile.setObjectName(u"label_icon_workfile")
        self.label_icon_workfile.setMaximumSize(QSize(18, 18))

        self.horizontalLayout_2.addWidget(self.label_icon_workfile)

        self.label_workfile = QLabel(self.frame_workfile)
        self.label_workfile.setObjectName(u"label_workfile")
        self.label_workfile.setMinimumSize(QSize(65, 0))
        self.label_workfile.setMaximumSize(QSize(65, 16777215))
        self.label_workfile.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.label_workfile)

        self.line_edit_workfile = QLineEdit(self.frame_workfile)
        self.line_edit_workfile.setObjectName(u"line_edit_workfile")
        self.line_edit_workfile.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.line_edit_workfile)


        self.verticalLayout_2.addWidget(self.frame_workfile)

        self.frame_path = QFrame(self.group_box_current)
        self.frame_path.setObjectName(u"frame_path")
        self.frame_path.setFrameShape(QFrame.NoFrame)
        self.frame_path.setFrameShadow(QFrame.Plain)
        self.frame_path.setLineWidth(0)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_path)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_icon_path = QLabel(self.frame_path)
        self.label_icon_path.setObjectName(u"label_icon_path")
        self.label_icon_path.setMaximumSize(QSize(18, 18))

        self.horizontalLayout_3.addWidget(self.label_icon_path)

        self.label_path = QLabel(self.frame_path)
        self.label_path.setObjectName(u"label_path")
        self.label_path.setMinimumSize(QSize(65, 0))
        self.label_path.setMaximumSize(QSize(65, 16777215))
        self.label_path.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.label_path)

        self.line_edit_path = QLineEdit(self.frame_path)
        self.line_edit_path.setObjectName(u"line_edit_path")
        self.line_edit_path.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.line_edit_path)


        self.verticalLayout_2.addWidget(self.frame_path)


        self.verticalLayout.addWidget(self.group_box_current)

        self.group_box_save = QGroupBox(Form)
        self.group_box_save.setObjectName(u"group_box_save")
        self.verticalLayout_3 = QVBoxLayout(self.group_box_save)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.frame_version = QFrame(self.group_box_save)
        self.frame_version.setObjectName(u"frame_version")
        self.frame_version.setFrameShape(QFrame.NoFrame)
        self.frame_version.setFrameShadow(QFrame.Plain)
        self.frame_version.setLineWidth(0)
        self.horizontalLayout = QHBoxLayout(self.frame_version)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_icon_version = QLabel(self.frame_version)
        self.label_icon_version.setObjectName(u"label_icon_version")
        self.label_icon_version.setMaximumSize(QSize(18, 18))

        self.horizontalLayout.addWidget(self.label_icon_version)

        self.label_version = QLabel(self.frame_version)
        self.label_version.setObjectName(u"label_version")
        self.label_version.setMinimumSize(QSize(65, 0))
        self.label_version.setMaximumSize(QSize(65, 16777215))
        self.label_version.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout.addWidget(self.label_version)

        self.spinbox_version = QSpinBox(self.frame_version)
        self.spinbox_version.setObjectName(u"spinbox_version")

        self.horizontalLayout.addWidget(self.spinbox_version)

        self.checkbox_next_available_version = QCheckBox(self.frame_version)
        self.checkbox_next_available_version.setObjectName(u"checkbox_next_available_version")
        self.checkbox_next_available_version.setChecked(True)

        self.horizontalLayout.addWidget(self.checkbox_next_available_version)


        self.verticalLayout_3.addWidget(self.frame_version)

        self.frame_to_save = QFrame(self.group_box_save)
        self.frame_to_save.setObjectName(u"frame_to_save")
        self.frame_to_save.setFrameShape(QFrame.NoFrame)
        self.frame_to_save.setFrameShadow(QFrame.Plain)
        self.frame_to_save.setLineWidth(0)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_to_save)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_icon_to_save = QLabel(self.frame_to_save)
        self.label_icon_to_save.setObjectName(u"label_icon_to_save")
        self.label_icon_to_save.setMaximumSize(QSize(18, 18))

        self.horizontalLayout_4.addWidget(self.label_icon_to_save)

        self.label_to_save = QLabel(self.frame_to_save)
        self.label_to_save.setObjectName(u"label_to_save")
        self.label_to_save.setMinimumSize(QSize(65, 0))
        self.label_to_save.setMaximumSize(QSize(65, 16777215))
        self.label_to_save.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_4.addWidget(self.label_to_save)

        self.line_edit_to_save = QLineEdit(self.frame_to_save)
        self.line_edit_to_save.setObjectName(u"line_edit_to_save")
        self.line_edit_to_save.setReadOnly(True)

        self.horizontalLayout_4.addWidget(self.line_edit_to_save)


        self.verticalLayout_3.addWidget(self.frame_to_save)

        self.frame_thumbnail = QFrame(self.group_box_save)
        self.frame_thumbnail.setObjectName(u"frame_thumbnail")
        self.frame_thumbnail.setFrameShape(QFrame.NoFrame)
        self.frame_thumbnail.setFrameShadow(QFrame.Plain)
        self.frame_thumbnail.setLineWidth(0)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_thumbnail)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.label_icon_thumbnail = QLabel(self.frame_thumbnail)
        self.label_icon_thumbnail.setObjectName(u"label_icon_thumbnail")
        self.label_icon_thumbnail.setMaximumSize(QSize(18, 18))

        self.horizontalLayout_5.addWidget(self.label_icon_thumbnail)

        self.label_thumbnail = QLabel(self.frame_thumbnail)
        self.label_thumbnail.setObjectName(u"label_thumbnail")
        self.label_thumbnail.setMinimumSize(QSize(65, 0))
        self.label_thumbnail.setMaximumSize(QSize(65, 16777215))
        self.label_thumbnail.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.label_thumbnail)

        self.line_edit_thumbnail = QLineEdit(self.frame_thumbnail)
        self.line_edit_thumbnail.setObjectName(u"line_edit_thumbnail")

        self.horizontalLayout_5.addWidget(self.line_edit_thumbnail)

        self.button_pick_thumbnail = QPushButton(self.frame_thumbnail)
        self.button_pick_thumbnail.setObjectName(u"button_pick_thumbnail")

        self.horizontalLayout_5.addWidget(self.button_pick_thumbnail)

        self.button_capture_thumbnail = QPushButton(self.frame_thumbnail)
        self.button_capture_thumbnail.setObjectName(u"button_capture_thumbnail")

        self.horizontalLayout_5.addWidget(self.button_capture_thumbnail)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.button_discard_thumbnail = QPushButton(self.frame_thumbnail)
        self.button_discard_thumbnail.setObjectName(u"button_discard_thumbnail")

        self.horizontalLayout_5.addWidget(self.button_discard_thumbnail)

        self.horizontalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_2)

        self.button_preview_thumbnail = QPushButton(self.frame_thumbnail)
        self.button_preview_thumbnail.setObjectName(u"button_preview_thumbnail")

        self.horizontalLayout_5.addWidget(self.button_preview_thumbnail)


        self.verticalLayout_3.addWidget(self.frame_thumbnail)

        self.frame_comment = QFrame(self.group_box_save)
        self.frame_comment.setObjectName(u"frame_comment")
        self.frame_comment.setFrameShape(QFrame.NoFrame)
        self.frame_comment.setFrameShadow(QFrame.Plain)
        self.frame_comment.setLineWidth(0)
        self.gridLayout = QGridLayout(self.frame_comment)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label_icon_comment = QLabel(self.frame_comment)
        self.label_icon_comment.setObjectName(u"label_icon_comment")
        self.label_icon_comment.setMaximumSize(QSize(18, 18))

        self.gridLayout.addWidget(self.label_icon_comment, 0, 0, 1, 1)

        self.label_comment = QLabel(self.frame_comment)
        self.label_comment.setObjectName(u"label_comment")
        self.label_comment.setMinimumSize(QSize(65, 0))
        self.label_comment.setMaximumSize(QSize(65, 16777215))
        self.label_comment.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_comment, 0, 1, 1, 1)

        self.text_edit_comment = QTextEdit(self.frame_comment)
        self.text_edit_comment.setObjectName(u"text_edit_comment")

        self.gridLayout.addWidget(self.text_edit_comment, 0, 2, 2, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 44, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.verticalSpacer_2, 1, 1, 1, 1)


        self.verticalLayout_3.addWidget(self.frame_comment)


        self.verticalLayout.addWidget(self.group_box_save)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.button_box = QDialogButtonBox(Form)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)

        self.verticalLayout.addWidget(self.button_box)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.group_box_current.setTitle(QCoreApplication.translate("Form", u"Current", None))
        self.label_icon_workfile.setText(QCoreApplication.translate("Form", u"Icon", None))
        self.label_workfile.setText(QCoreApplication.translate("Form", u"Workfile", None))
        self.line_edit_workfile.setPlaceholderText(QCoreApplication.translate("Form", u"Workfile...", None))
        self.label_icon_path.setText(QCoreApplication.translate("Form", u"Icon", None))
        self.label_path.setText(QCoreApplication.translate("Form", u"Path", None))
        self.line_edit_path.setPlaceholderText(QCoreApplication.translate("Form", u"Path...", None))
        self.group_box_save.setTitle(QCoreApplication.translate("Form", u"Save", None))
        self.label_icon_version.setText(QCoreApplication.translate("Form", u"Icon", None))
        self.label_version.setText(QCoreApplication.translate("Form", u"Version", None))
        self.checkbox_next_available_version.setText(QCoreApplication.translate("Form", u"Next Available Version", None))
        self.label_icon_to_save.setText(QCoreApplication.translate("Form", u"Icon", None))
        self.label_to_save.setText(QCoreApplication.translate("Form", u"To Save", None))
        self.line_edit_to_save.setPlaceholderText(QCoreApplication.translate("Form", u"Path...", None))
        self.label_icon_thumbnail.setText(QCoreApplication.translate("Form", u"Icon", None))
        self.label_thumbnail.setText(QCoreApplication.translate("Form", u"Thumbnail", None))
#if QT_CONFIG(tooltip)
        self.line_edit_thumbnail.setToolTip(QCoreApplication.translate("Form", u"<b>Thumbnail</b><hr>Choose the thumbnail image that will be displayed.", None))
#endif // QT_CONFIG(tooltip)
        self.line_edit_thumbnail.setPlaceholderText(QCoreApplication.translate("Form", u"Thumbnail...", None))
        self.button_pick_thumbnail.setText(QCoreApplication.translate("Form", u"Pick", None))
        self.button_capture_thumbnail.setText(QCoreApplication.translate("Form", u"Capture", None))
        self.button_discard_thumbnail.setText(QCoreApplication.translate("Form", u"Discard", None))
        self.button_preview_thumbnail.setText(QCoreApplication.translate("Form", u"Preview", None))
        self.label_icon_comment.setText(QCoreApplication.translate("Form", u"Icon", None))
        self.label_comment.setText(QCoreApplication.translate("Form", u"Comment", None))
        self.text_edit_comment.setPlaceholderText(QCoreApplication.translate("Form", u"Comment...", None))
    # retranslateUi

