# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'create_task.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialogButtonBox, QGridLayout,
    QListWidget, QListWidgetItem, QSizePolicy, QWidget)

class Ui_FXCreateTask(object):
    def setupUi(self, FXCreateTask):
        if not FXCreateTask.objectName():
            FXCreateTask.setObjectName(u"FXCreateTask")
        FXCreateTask.resize(414, 502)
        self.gridLayout = QGridLayout(FXCreateTask)
        self.gridLayout.setObjectName(u"gridLayout")
        self.list_tasks = QListWidget(FXCreateTask)
        self.list_tasks.setObjectName(u"list_tasks")

        self.gridLayout.addWidget(self.list_tasks, 0, 0, 1, 1)

        self.button_box = QDialogButtonBox(FXCreateTask)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.button_box, 1, 0, 1, 1)


        self.retranslateUi(FXCreateTask)

        QMetaObject.connectSlotsByName(FXCreateTask)
    # setupUi

    def retranslateUi(self, FXCreateTask):
        FXCreateTask.setWindowTitle(QCoreApplication.translate("FXCreateTask", u"Form", None))
    # retranslateUi

