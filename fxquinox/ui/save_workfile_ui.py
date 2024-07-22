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
    QFrame, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(743, 242)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame_version = QFrame(Form)
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


        self.verticalLayout.addWidget(self.frame_version)

        self.line = QFrame(Form)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.frame_workfile = QFrame(Form)
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


        self.verticalLayout.addWidget(self.frame_workfile)

        self.frame_path = QFrame(Form)
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


        self.verticalLayout.addWidget(self.frame_path)

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
        self.label_icon_version.setText(QCoreApplication.translate("Form", u"Icon", None))
        self.label_version.setText(QCoreApplication.translate("Form", u"Version", None))
        self.checkbox_next_available_version.setText(QCoreApplication.translate("Form", u"Next Available Version", None))
        self.label_icon_workfile.setText(QCoreApplication.translate("Form", u"Icon", None))
        self.label_workfile.setText(QCoreApplication.translate("Form", u"Workfile", None))
        self.line_edit_workfile.setPlaceholderText(QCoreApplication.translate("Form", u"Workfile...", None))
        self.label_icon_path.setText(QCoreApplication.translate("Form", u"Icon", None))
        self.label_path.setText(QCoreApplication.translate("Form", u"Path", None))
        self.line_edit_path.setPlaceholderText(QCoreApplication.translate("Form", u"Path...", None))
    # retranslateUi

