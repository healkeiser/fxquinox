# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'create_step.ui'
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
    QGridLayout, QListWidget, QListWidgetItem, QSizePolicy,
    QSpacerItem, QWidget)

class Ui_FXCreateStep(object):
    def setupUi(self, FXCreateStep):
        if not FXCreateStep.objectName():
            FXCreateStep.setObjectName(u"FXCreateStep")
        FXCreateStep.resize(400, 500)
        self.gridLayout = QGridLayout(FXCreateStep)
        self.gridLayout.setObjectName(u"gridLayout")
        self.list_steps = QListWidget(FXCreateStep)
        self.list_steps.setObjectName(u"list_steps")

        self.gridLayout.addWidget(self.list_steps, 0, 0, 1, 2)

        self.checkbox_add_tasks = QCheckBox(FXCreateStep)
        self.checkbox_add_tasks.setObjectName(u"checkbox_add_tasks")
        self.checkbox_add_tasks.setChecked(True)

        self.gridLayout.addWidget(self.checkbox_add_tasks, 1, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(301, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 1, 1, 1)

        self.button_box = QDialogButtonBox(FXCreateStep)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.button_box, 3, 0, 1, 2)

        self.list_tasks = QListWidget(FXCreateStep)
        self.list_tasks.setObjectName(u"list_tasks")
        self.list_tasks.setMaximumSize(QSize(16777215, 150))

        self.gridLayout.addWidget(self.list_tasks, 2, 0, 1, 2)


        self.retranslateUi(FXCreateStep)

        QMetaObject.connectSlotsByName(FXCreateStep)
    # setupUi

    def retranslateUi(self, FXCreateStep):
        FXCreateStep.setWindowTitle(QCoreApplication.translate("FXCreateStep", u"Form", None))
        self.checkbox_add_tasks.setText(QCoreApplication.translate("FXCreateStep", u"Add Tasks", None))
    # retranslateUi

