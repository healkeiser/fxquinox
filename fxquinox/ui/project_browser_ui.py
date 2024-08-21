# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'project_browser.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QListView, QListWidget, QListWidgetItem,
    QSizePolicy, QSpacerItem, QSplitter, QTabWidget,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

class Ui_FXProjectBrowser(object):
    def setupUi(self, FXProjectBrowser):
        if not FXProjectBrowser.objectName():
            FXProjectBrowser.setObjectName(u"FXProjectBrowser")
        FXProjectBrowser.resize(2067, 852)
        self.verticalLayout_7 = QVBoxLayout(FXProjectBrowser)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.frame_project = QFrame(FXProjectBrowser)
        self.frame_project.setObjectName(u"frame_project")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_project.sizePolicy().hasHeightForWidth())
        self.frame_project.setSizePolicy(sizePolicy)
        self.frame_project.setFrameShape(QFrame.NoFrame)
        self.frame_project.setFrameShadow(QFrame.Plain)
        self.frame_project.setLineWidth(0)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_project)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_project = QLabel(self.frame_project)
        self.label_project.setObjectName(u"label_project")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_project.sizePolicy().hasHeightForWidth())
        self.label_project.setSizePolicy(sizePolicy1)

        self.horizontalLayout_3.addWidget(self.label_project)

        self.line_project = QFrame(self.frame_project)
        self.line_project.setObjectName(u"line_project")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.line_project.sizePolicy().hasHeightForWidth())
        self.line_project.setSizePolicy(sizePolicy2)
        self.line_project.setFrameShape(QFrame.Shape.HLine)
        self.line_project.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_3.addWidget(self.line_project)


        self.verticalLayout_7.addWidget(self.frame_project)

        self.splitter = QSplitter(FXProjectBrowser)
        self.splitter.setObjectName(u"splitter")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy3)
        self.splitter.setOrientation(Qt.Horizontal)
        self.tab_assets_shots = QTabWidget(self.splitter)
        self.tab_assets_shots.setObjectName(u"tab_assets_shots")
        self.tab_assets = QWidget()
        self.tab_assets.setObjectName(u"tab_assets")
        self.verticalLayout_2 = QVBoxLayout(self.tab_assets)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame_filter_assets = QFrame(self.tab_assets)
        self.frame_filter_assets.setObjectName(u"frame_filter_assets")
        self.frame_filter_assets.setFrameShape(QFrame.NoFrame)
        self.frame_filter_assets.setFrameShadow(QFrame.Plain)
        self.frame_filter_assets.setLineWidth(0)
        self.horizontalLayout = QHBoxLayout(self.frame_filter_assets)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_icon_filter_assets = QLabel(self.frame_filter_assets)
        self.label_icon_filter_assets.setObjectName(u"label_icon_filter_assets")
        self.label_icon_filter_assets.setMaximumSize(QSize(18, 18))

        self.horizontalLayout.addWidget(self.label_icon_filter_assets)

        self.line_edit_filter_assets = QLineEdit(self.frame_filter_assets)
        self.line_edit_filter_assets.setObjectName(u"line_edit_filter_assets")

        self.horizontalLayout.addWidget(self.line_edit_filter_assets)


        self.verticalLayout_2.addWidget(self.frame_filter_assets)

        self.tree_widget_assets = QTreeWidget(self.tab_assets)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"Assets");
        self.tree_widget_assets.setHeaderItem(__qtreewidgetitem)
        self.tree_widget_assets.setObjectName(u"tree_widget_assets")
        self.tree_widget_assets.setAlternatingRowColors(True)

        self.verticalLayout_2.addWidget(self.tree_widget_assets)

        self.tab_assets_shots.addTab(self.tab_assets, "")
        self.tab_shots = QWidget()
        self.tab_shots.setObjectName(u"tab_shots")
        self.verticalLayout = QVBoxLayout(self.tab_shots)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame_filter_shots = QFrame(self.tab_shots)
        self.frame_filter_shots.setObjectName(u"frame_filter_shots")
        self.frame_filter_shots.setFrameShape(QFrame.NoFrame)
        self.frame_filter_shots.setFrameShadow(QFrame.Plain)
        self.frame_filter_shots.setLineWidth(0)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_filter_shots)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_icon_filter_shots = QLabel(self.frame_filter_shots)
        self.label_icon_filter_shots.setObjectName(u"label_icon_filter_shots")
        self.label_icon_filter_shots.setMaximumSize(QSize(18, 18))

        self.horizontalLayout_2.addWidget(self.label_icon_filter_shots)

        self.line_edit_filter_shots = QLineEdit(self.frame_filter_shots)
        self.line_edit_filter_shots.setObjectName(u"line_edit_filter_shots")

        self.horizontalLayout_2.addWidget(self.line_edit_filter_shots)


        self.verticalLayout.addWidget(self.frame_filter_shots)

        self.tree_widget_shots = QTreeWidget(self.tab_shots)
        __qtreewidgetitem1 = QTreeWidgetItem()
        __qtreewidgetitem1.setText(0, u"Shots");
        self.tree_widget_shots.setHeaderItem(__qtreewidgetitem1)
        self.tree_widget_shots.setObjectName(u"tree_widget_shots")
        self.tree_widget_shots.setUniformRowHeights(False)
        self.tree_widget_shots.setAnimated(True)

        self.verticalLayout.addWidget(self.tree_widget_shots)

        self.tab_assets_shots.addTab(self.tab_shots, "")
        self.splitter.addWidget(self.tab_assets_shots)
        self.splitters_steps_tasks_info = QSplitter(self.splitter)
        self.splitters_steps_tasks_info.setObjectName(u"splitters_steps_tasks_info")
        self.splitters_steps_tasks_info.setOrientation(Qt.Vertical)
        self.splitters_steps_tasks = QSplitter(self.splitters_steps_tasks_info)
        self.splitters_steps_tasks.setObjectName(u"splitters_steps_tasks")
        self.splitters_steps_tasks.setOrientation(Qt.Horizontal)
        self.group_box_steps = QGroupBox(self.splitters_steps_tasks)
        self.group_box_steps.setObjectName(u"group_box_steps")
        self.verticalLayout_3 = QVBoxLayout(self.group_box_steps)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.list_steps = QListWidget(self.group_box_steps)
        self.list_steps.setObjectName(u"list_steps")
        self.list_steps.setLayoutMode(QListView.Batched)
        self.list_steps.setUniformItemSizes(True)
        self.list_steps.setSortingEnabled(True)

        self.verticalLayout_3.addWidget(self.list_steps)

        self.splitters_steps_tasks.addWidget(self.group_box_steps)
        self.group_box_tasks = QGroupBox(self.splitters_steps_tasks)
        self.group_box_tasks.setObjectName(u"group_box_tasks")
        self.verticalLayout_4 = QVBoxLayout(self.group_box_tasks)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.list_tasks = QListWidget(self.group_box_tasks)
        self.list_tasks.setObjectName(u"list_tasks")
        self.list_tasks.setLayoutMode(QListView.Batched)
        self.list_tasks.setUniformItemSizes(True)
        self.list_tasks.setSortingEnabled(True)

        self.verticalLayout_4.addWidget(self.list_tasks)

        self.splitters_steps_tasks.addWidget(self.group_box_tasks)
        self.splitters_steps_tasks_info.addWidget(self.splitters_steps_tasks)
        self.group_box_info = QGroupBox(self.splitters_steps_tasks_info)
        self.group_box_info.setObjectName(u"group_box_info")
        self.verticalLayout_6 = QVBoxLayout(self.group_box_info)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.splitters_steps_tasks_info.addWidget(self.group_box_info)
        self.splitter.addWidget(self.splitters_steps_tasks_info)
        self.group_box_workfiles = QGroupBox(self.splitter)
        self.group_box_workfiles.setObjectName(u"group_box_workfiles")
        self.verticalLayout_5 = QVBoxLayout(self.group_box_workfiles)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.frame = QFrame(self.group_box_workfiles)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Plain)
        self.frame.setLineWidth(0)
        self.horizontalLayout_4 = QHBoxLayout(self.frame)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.checkbox_display_latest_workfiles = QCheckBox(self.frame)
        self.checkbox_display_latest_workfiles.setObjectName(u"checkbox_display_latest_workfiles")

        self.horizontalLayout_4.addWidget(self.checkbox_display_latest_workfiles)

        self.horizontalSpacer = QSpacerItem(271, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.label_icon_filter_workfiles = QLabel(self.frame)
        self.label_icon_filter_workfiles.setObjectName(u"label_icon_filter_workfiles")
        self.label_icon_filter_workfiles.setMaximumSize(QSize(18, 18))

        self.horizontalLayout_4.addWidget(self.label_icon_filter_workfiles)

        self.combobox_filter_workfiles = QComboBox(self.frame)
        self.combobox_filter_workfiles.addItem("")
        self.combobox_filter_workfiles.addItem("")
        self.combobox_filter_workfiles.addItem("")
        self.combobox_filter_workfiles.addItem("")
        self.combobox_filter_workfiles.addItem("")
        self.combobox_filter_workfiles.addItem("")
        self.combobox_filter_workfiles.addItem("")
        self.combobox_filter_workfiles.setObjectName(u"combobox_filter_workfiles")

        self.horizontalLayout_4.addWidget(self.combobox_filter_workfiles)


        self.verticalLayout_5.addWidget(self.frame)

        self.tree_widget_workfiles = QTreeWidget(self.group_box_workfiles)
        __qtreewidgetitem2 = QTreeWidgetItem()
        __qtreewidgetitem2.setText(0, u"Workfile");
        self.tree_widget_workfiles.setHeaderItem(__qtreewidgetitem2)
        self.tree_widget_workfiles.setObjectName(u"tree_widget_workfiles")
        self.tree_widget_workfiles.setAlternatingRowColors(True)
        self.tree_widget_workfiles.setRootIsDecorated(False)
        self.tree_widget_workfiles.setUniformRowHeights(True)
        self.tree_widget_workfiles.setItemsExpandable(False)
        self.tree_widget_workfiles.setSortingEnabled(True)
        self.tree_widget_workfiles.setAnimated(True)

        self.verticalLayout_5.addWidget(self.tree_widget_workfiles)

        self.splitter.addWidget(self.group_box_workfiles)

        self.verticalLayout_7.addWidget(self.splitter)


        self.retranslateUi(FXProjectBrowser)

        self.tab_assets_shots.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(FXProjectBrowser)
    # setupUi

    def retranslateUi(self, FXProjectBrowser):
        FXProjectBrowser.setWindowTitle(QCoreApplication.translate("FXProjectBrowser", u"Form", None))
        self.label_project.setText(QCoreApplication.translate("FXProjectBrowser", u"Project", None))
#if QT_CONFIG(tooltip)
        self.tab_assets_shots.setToolTip(QCoreApplication.translate("FXProjectBrowser", u"<b>Filter Assets</b><hr>Filter the assets by name.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.tab_assets_shots.setStatusTip(QCoreApplication.translate("FXProjectBrowser", u"Filter the assets by name", None))
#endif // QT_CONFIG(statustip)
        self.label_icon_filter_assets.setText(QCoreApplication.translate("FXProjectBrowser", u"Icon", None))
        self.line_edit_filter_assets.setPlaceholderText(QCoreApplication.translate("FXProjectBrowser", u"Filter...", None))
#if QT_CONFIG(tooltip)
        self.tree_widget_assets.setToolTip(QCoreApplication.translate("FXProjectBrowser", u"<b>Assets</b><hr>A tree of the existing assets.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.tree_widget_assets.setStatusTip(QCoreApplication.translate("FXProjectBrowser", u"A tree of the existing assets", None))
#endif // QT_CONFIG(statustip)
        self.tab_assets_shots.setTabText(self.tab_assets_shots.indexOf(self.tab_assets), QCoreApplication.translate("FXProjectBrowser", u"Assets", None))
        self.label_icon_filter_shots.setText(QCoreApplication.translate("FXProjectBrowser", u"Icon", None))
#if QT_CONFIG(tooltip)
        self.line_edit_filter_shots.setToolTip(QCoreApplication.translate("FXProjectBrowser", u"<b>Filter Shots</b><hr>Filter the shots by name.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.line_edit_filter_shots.setStatusTip(QCoreApplication.translate("FXProjectBrowser", u"Filter the shots by name", None))
#endif // QT_CONFIG(statustip)
        self.line_edit_filter_shots.setPlaceholderText(QCoreApplication.translate("FXProjectBrowser", u"Filter...", None))
#if QT_CONFIG(tooltip)
        self.tree_widget_shots.setToolTip(QCoreApplication.translate("FXProjectBrowser", u"<b>Shots</b><hr>A tree of the existing sequences and their shots.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.tree_widget_shots.setStatusTip(QCoreApplication.translate("FXProjectBrowser", u"A tree of the existing sequences and their shots", None))
#endif // QT_CONFIG(statustip)
        self.tab_assets_shots.setTabText(self.tab_assets_shots.indexOf(self.tab_shots), QCoreApplication.translate("FXProjectBrowser", u"Shots", None))
        self.group_box_steps.setTitle(QCoreApplication.translate("FXProjectBrowser", u"Steps", None))
        self.group_box_tasks.setTitle(QCoreApplication.translate("FXProjectBrowser", u"Tasks", None))
        self.group_box_info.setTitle(QCoreApplication.translate("FXProjectBrowser", u"Metadata", None))
        self.group_box_workfiles.setTitle(QCoreApplication.translate("FXProjectBrowser", u"Workfiles", None))
        self.checkbox_display_latest_workfiles.setText(QCoreApplication.translate("FXProjectBrowser", u"Show Only Latest", None))
        self.label_icon_filter_workfiles.setText(QCoreApplication.translate("FXProjectBrowser", u"Icon", None))
        self.combobox_filter_workfiles.setItemText(0, QCoreApplication.translate("FXProjectBrowser", u"All", None))
        self.combobox_filter_workfiles.setItemText(1, QCoreApplication.translate("FXProjectBrowser", u"Blender", None))
        self.combobox_filter_workfiles.setItemText(2, QCoreApplication.translate("FXProjectBrowser", u"Houdini", None))
        self.combobox_filter_workfiles.setItemText(3, QCoreApplication.translate("FXProjectBrowser", u"Maya", None))
        self.combobox_filter_workfiles.setItemText(4, QCoreApplication.translate("FXProjectBrowser", u"Nuke", None))
        self.combobox_filter_workfiles.setItemText(5, QCoreApplication.translate("FXProjectBrowser", u"Photoshop", None))
        self.combobox_filter_workfiles.setItemText(6, QCoreApplication.translate("FXProjectBrowser", u"Substance Painter", None))

        ___qtreewidgetitem = self.tree_widget_workfiles.headerItem()
        ___qtreewidgetitem.setText(6, QCoreApplication.translate("FXProjectBrowser", u"Size", None));
        ___qtreewidgetitem.setText(5, QCoreApplication.translate("FXProjectBrowser", u"User", None));
        ___qtreewidgetitem.setText(4, QCoreApplication.translate("FXProjectBrowser", u"Date Modified", None));
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("FXProjectBrowser", u"Date Created", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("FXProjectBrowser", u"Comment", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("FXProjectBrowser", u"Version", None));
    # retranslateUi

