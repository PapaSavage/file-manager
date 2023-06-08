import typing
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QWidget
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, QItemSelectionModel, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QTreeView, QStyledItemDelegate
from threading import Thread
from pathlib import Path
import os
import sys
import subprocess
import shutil
import errno
import psutil
from PyQt5.QtWidgets import (
    QTreeView,
    QApplication,
    QDialog,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt, QMimeData, QDir, QFile, QFileInfo
import time


class DeleteThread(QThread):
    update_progress = pyqtSignal(int)

    def __init__(self, fileModel, index):
        super().__init__()
        self.fileModel = fileModel
        self.index = index

    def run(self):
        total_files = len(self.index)
        progress_step = 100 / total_files
        progress = 0

        for delFile in self.index:
            QtCore.QCoreApplication.processEvents()
            self.fileModel.remove(delFile)

            progress += progress_step
            self.update_progress.emit(int(progress))

        self.update_progress.emit(100)


class ProgressDialog(QDialog):
    def __init__(self, fileModel, index, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Process")
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)

        self.text = QtWidgets.QLabel()
        # self.text.setAlignment(che)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setText("Deleting items")

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

        self.delete_thread = DeleteThread(fileModel, index)
        self.delete_thread.update_progress.connect(self.update_progress)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_ui(self):
        if self.progress_bar.value() == 100:
            self.timer.stop()
            time.sleep(0.5)
            self.close()

    def start_deletion(self):
        self.delete_thread.start()

    def cancel(self):
        self.delete_thread.requestInterruption()
        self.delete_thread.quit()
        self.delete_thread.wait()
        self.progress_bar.reset()


class PasteThread(QThread):
    update_progress = pyqtSignal(int)

    def __init__(self, destTarg):
        super().__init__()
        self.destTarg = destTarg

    def run(self):
        total_files = len(self.destTarg) / 2
        progress_step = 100 / total_files
        progress = 0

        for i in range(0, len(self.destTarg), 2):
            self.target = self.destTarg[i]
            self.destination = self.destTarg[i + 1]

            try:
                shutil.copytree(self.target, self.destination)
            except OSError as e:
                if e.errno == errno.ENOTDIR:
                    shutil.copy(self.target, self.destination)

            progress += progress_step
            self.update_progress.emit(int(progress))
        self.update_progress.emit(100)


class ProgressDialog_Paste(QDialog):
    def __init__(self, destTarg, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Proceess")

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)

        self.text = QtWidgets.QLabel()
        # self.text.setAlignment(che)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setText("Pasting items")

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

        self.paste_thread = PasteThread(destTarg)
        self.paste_thread.update_progress.connect(self.update_progress)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_ui(self):
        if self.progress_bar.value() == 100:
            self.timer.stop()
            time.sleep(0.5)
            self.close()

    def start_pasting(self):
        self.paste_thread.start()

    def cancel(self):
        self.paste_thread.terminate()
        self.progress_bar.reset()


class Errors:
    def itemnotExist(self):
        dlg = QMessageBox()
        dlg.setWindowTitle("Ошибка")
        dlg.setText("Файла для копирования не существует")
        button = dlg.exec()

    def cutIn(self):
        dlg = QMessageBox()
        dlg.setWindowTitle("Ошибка")
        dlg.setText("Вырезанный объект нельзя вставить в себя")
        button = dlg.exec()


class DragDropTreeView(QTreeView):
    def __init__(self, parent=None):
        super(DragDropTreeView, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(self.InternalMove)

    def startDrag(self, supportedActions):
        index = self.currentIndex()
        if not index.isValid():
            return

        mimedata = self.model().mimeData([index])
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimedata)
        drag.exec_(supportedActions)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            urls = [url.toLocalFile() for url in event.mimeData().urls()]
            destination_index = self.indexAt(event.pos())
            destination_path = self.model().filePath(destination_index)
            for url in urls:
                file_info = QFileInfo(url)
                if file_info.isFile():
                    new_file_path = QDir(destination_path).filePath(
                        file_info.fileName()
                    )
                elif file_info.isDir():
                    new_folder_path = QDir(destination_path).filePath(
                        file_info.fileName()
                    )


class StyledItemDelegate(QStyledItemDelegate):
    def __init__(self, indexes) -> None:
        super().__init__()
        self.indexes = indexes

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        # Проверяем условие, когда нужно изменить стиль строки
        if index in self.indexes:
            option.font.setBold(True)


class StyledItemDelegate_cancel(QStyledItemDelegate):
    def __init__(self, indexes) -> None:
        super().__init__()
        self.indexes = indexes

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        # Проверяем условие, когда нужно изменить стиль строки
        if index in self.indexes:
            option.font.setBold(False)


class ClssDialog(QtWidgets.QDialog):
    pathEntered = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(ClssDialog, self).__init__(parent)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.pathbar_left = QtWidgets.QLineEdit()
        self.pathbar_left.setMinimumSize(QtCore.QSize(50, 20))
        self.pathbar_left.setObjectName("pathbar_left")

        self.verticalLayout.addWidget(self.pathbar_left)

        self.pathbar_left.returnPressed.connect(self.handleReturnPressed)

        self.setWindowTitle("Finding")

    def handleReturnPressed(self):
        if (os.path.exists(self.pathbar_left.text())) or (
            self.pathbar_left.text() == ""
        ):
            self.pathEntered.emit(self.pathbar_left.text())
            self.close()

        else:
            dlg = QMessageBox()
            dlg.setWindowTitle("Ошибка")
            dlg.setText("Неверный адрес")
            button = dlg.exec()

            if button == QMessageBox.Ok:
                print("Я понял")

            # print(os.path.exists(self.pathbar_left.text()))

    def showEvent(self, event):
        super(ClssDialog, self).showEvent(event)
        self.pathbar_left.setFocus()
        self.pathbar_left.selectAll()
        screen_geometry = QtWidgets.QApplication.desktop().screenGeometry()
        dialog_geometry = self.geometry()
        x = (screen_geometry.width() - dialog_geometry.width()) // 2
        y = (screen_geometry.height() - dialog_geometry.height()) // 2
        self.move(x, y)


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setObjectName("MainWindow")
        self.resize(1337, 631)

        self.setStyleSheet(mystylesheetdark(self))

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.backbutton_left = QtWidgets.QPushButton(self.centralwidget)
        self.backbutton_left.setMaximumSize(QtCore.QSize(100, 100))
        self.backbutton_left.setMaximumSize(QtCore.QSize(25, 25))

        self.backbutton_left.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("src/left-arrow.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.backbutton_left.setIcon(icon)
        self.backbutton_left.setObjectName("backbutton_left")
        self.backbutton_left.clicked.connect(self.back_click_left)

        self.horizontalLayout_2.addWidget(self.backbutton_left)

        self.upbutton_left = QtWidgets.QPushButton(self.centralwidget)
        self.upbutton_left.setMaximumSize(QtCore.QSize(25, 25))
        self.upbutton_left.setStyleSheet("")
        self.upbutton_left.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap("src/up-arrow.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )

        self.upbutton_left.setIcon(icon1)
        self.upbutton_left.setObjectName("upbutton_left")
        self.upbutton_left.clicked.connect(self.goUp_click_left)

        self.horizontalLayout_2.addWidget(self.upbutton_left)

        self.pathbar_left = QtWidgets.QLineEdit(self.centralwidget)
        self.pathbar_left.setReadOnly(True)
        self.pathbar_left.setObjectName("pathbar_left")
        self.pathbar_left.setText("Drives")
        self.horizontalLayout_2.addWidget(self.pathbar_left)

        self.toolButton_left = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_left.setObjectName("toolButton_left")

        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("src/3points.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )

        self.toolButton_left.setIcon(icon)
        self.toolButton_left.clicked.connect(self.show_menu_left)
        self.menu_left = QtWidgets.QMenu(self.toolButton_left)
        self.actions_left = self.create_ToolBar_actions_left()
        self.menu_left.addActions(self.actions_left)
        self.toolButton_left.setMenu(self.menu_left)
        self.horizontalLayout_2.addWidget(self.toolButton_left)

        self.dialog_left = ClssDialog(self)
        self.dialog_left.pathEntered.connect(self.handlePathEntered_left)
        self.dialog_left.setMinimumWidth(320)

        self.pathbar_left.mousePressEvent = self.openDialog_left

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.dirModel_left = QtWidgets.QFileSystemModel()
        self.dirModel_left.setReadOnly(False)
        self.dirModel_left.setRootPath("")

        self.fileModel_left = QtWidgets.QFileSystemModel()
        self.fileModel_left.setReadOnly(False)
        self.fileModel_left.setRootPath("")

        self.treeview_left = QtWidgets.QTreeView(self.centralwidget)
        self.treeview_left.setMaximumSize(QtCore.QSize(250, 16777215))
        self.treeview_left.setObjectName("treeview_left")

        self.listview_left = QtWidgets.QTreeView(self.centralwidget)
        self.listview_left.setObjectName("listview_left")

        self.treeview_left.setModel(self.dirModel_left)
        self.listview_left.setModel(self.fileModel_left)

        self.treeview_left.hideColumn(1)
        self.treeview_left.hideColumn(2)
        self.treeview_left.hideColumn(3)
        self.treeview_left.setRootIsDecorated(True)
        self.treeview_left.setExpandsOnDoubleClick(True)
        self.treeview_left.setIndentation(12)
        self.treeview_left.setTreePosition(0)
        self.treeview_left.setUniformRowHeights(True)
        self.treeview_left.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.treeview_left.setDragEnabled(True)
        self.treeview_left.setAcceptDrops(True)
        self.treeview_left.setDropIndicatorShown(True)
        self.treeview_left.setAnimated(True)
        self.treeview_left.setSortingEnabled(True)
        self.treeview_left.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.treeview_left.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.listview_left.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.listview_left.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.listview_left.setAnimated(True)
        self.listview_left.setDragEnabled(True)
        self.listview_left.setAcceptDrops(True)
        self.listview_left.setDropIndicatorShown(True)
        self.listview_left.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.listview_left.setSortingEnabled(True)
        self.listview_left.header().resizeSection(0, 160)
        self.listview_left.header().resizeSection(1, 60)
        self.listview_left.header().resizeSection(2, 60)
        self.listview_left.header().resizeSection(3, 60)
        self.listview_left.setIndentation(12)
        self.listview_left.setExpandsOnDoubleClick(True)

        self.listview_left.doubleClicked.connect(self.list_doubleClicked_left)
        self.treeview_left.doubleClicked.connect(self.tree_doubleClicked_left)
        self.treeview_left.selectionModel().selectionChanged.connect(
            self.on_selectionChanged_left
        )

        self.splitter_left = QtWidgets.QSplitter()
        self.splitter_left.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_left.addWidget(self.treeview_left)
        self.splitter_left.addWidget(self.listview_left)

        self.verticalLayout.addWidget(self.splitter_left)
        self.horizontalLayout_5.addLayout(self.verticalLayout)

        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")

        self.toolButton_right = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_right.setObjectName("toolButton_right")

        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("src/3points.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )

        self.toolButton_right.setIcon(icon)

        self.menu_right = QtWidgets.QMenu(self.toolButton_right)
        self.actions_right = self.create_ToolBar_actions_left()
        self.menu_right.addActions(self.actions_right)
        self.toolButton_right.setMenu(self.menu_right)
        self.toolButton_right.clicked.connect(self.show_menu_right)

        self.horizontalLayout_8.addWidget(self.toolButton_right)

        self.pathbar_right = QtWidgets.QLineEdit(self.centralwidget)
        self.pathbar_right.setReadOnly(True)
        self.pathbar_right.setObjectName("pathbar_right")
        self.pathbar_right.setText("Drives")
        self.horizontalLayout_8.addWidget(self.pathbar_right)

        self.pathbar_right.mousePressEvent = self.openDialog_right

        self.dialog_right = ClssDialog(self)
        self.dialog_right.pathEntered.connect(self.handlePathEntered_right)
        self.dialog_right.setMinimumWidth(320)

        self.backbutton_right = QtWidgets.QPushButton(self.centralwidget)
        self.backbutton_right.setMaximumSize(QtCore.QSize(25, 25))
        self.backbutton_right.setText("")
        self.backbutton_right.setObjectName("backbutton_right")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("src/left-arrow.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.backbutton_right.setIcon(icon)
        self.backbutton_right.clicked.connect(self.back_click_right)

        self.horizontalLayout_8.addWidget(self.backbutton_right)

        self.upbutton_right = QtWidgets.QPushButton(self.centralwidget)
        self.upbutton_right.setMaximumSize(QtCore.QSize(25, 25))
        self.upbutton_right.setText("")
        self.upbutton_right.setObjectName("upbutton_right")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("src/up-arrow.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.upbutton_right.setIcon(icon)
        self.upbutton_right.clicked.connect(self.goUp_click_right)

        self.horizontalLayout_8.addWidget(self.upbutton_right)

        self.verticalLayout_3.addLayout(self.horizontalLayout_8)

        # self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        # self.horizontalLayout_7.setObjectName("horizontalLayout_7")

        self.dirModel_right = QtWidgets.QFileSystemModel()
        self.dirModel_right.setReadOnly(False)
        self.dirModel_right.setRootPath("")

        self.fileModel_right = QtWidgets.QFileSystemModel()
        self.fileModel_right.setReadOnly(False)
        self.fileModel_right.setRootPath("")

        self.listview_right = QtWidgets.QTreeView(self.centralwidget)
        self.listview_right.setObjectName("listview_right")
        # self.horizontalLayout_7.addWidget(self.listview_right)

        self.treeview_right = QtWidgets.QTreeView(self.centralwidget)
        self.treeview_right.setMaximumSize(QtCore.QSize(250, 16777215))
        self.treeview_right.setObjectName("treeview_right")
        # self.horizontalLayout_7.addWidget(self.treeview_right)

        self.treeview_right.setModel(self.dirModel_right)
        self.listview_right.setModel(self.fileModel_right)

        self.treeview_right.hideColumn(1)
        self.treeview_right.hideColumn(2)
        self.treeview_right.hideColumn(3)
        self.treeview_right.setRootIsDecorated(True)
        self.treeview_right.setExpandsOnDoubleClick(True)
        self.treeview_right.setIndentation(12)
        self.treeview_right.setTreePosition(0)
        self.treeview_right.setUniformRowHeights(True)
        self.treeview_right.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.treeview_right.setDragEnabled(True)
        self.treeview_right.setAcceptDrops(True)
        self.treeview_right.setDropIndicatorShown(True)
        self.treeview_right.setAnimated(True)
        self.treeview_right.setSortingEnabled(True)
        self.treeview_right.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.treeview_right.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.listview_right.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.listview_right.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.listview_right.setSortingEnabled(True)
        self.listview_right.setAnimated(True)
        self.listview_right.setDragEnabled(True)
        self.listview_right.setAcceptDrops(True)
        self.listview_right.setDropIndicatorShown(True)
        self.listview_right.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.listview_right.header().resizeSection(0, 160)
        self.listview_right.header().resizeSection(1, 60)
        self.listview_right.header().resizeSection(2, 60)
        self.listview_right.header().resizeSection(3, 60)
        self.listview_right.setIndentation(12)
        self.listview_right.setExpandsOnDoubleClick(True)

        self.listview_right.doubleClicked.connect(self.list_doubleClicked_right)
        self.treeview_right.doubleClicked.connect(self.tree_doubleClicked_right)
        self.treeview_right.selectionModel().selectionChanged.connect(
            self.on_selectionChanged_right
        )

        self.splitter_right = QtWidgets.QSplitter()
        self.splitter_right.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_right.addWidget(self.listview_right)
        self.splitter_right.addWidget(self.treeview_right)

        self.verticalLayout_3.addWidget(self.splitter_right)
        self.horizontalLayout_5.addLayout(self.verticalLayout_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_3.addItem(spacerItem)

        self.hiddenbutton = QtWidgets.QPushButton(self.centralwidget)
        self.hiddenbutton.setMinimumSize(QtCore.QSize(0, 0))
        self.hiddenbutton.setMaximumSize(QtCore.QSize(25, 25))
        self.hiddenbutton.setSizeIncrement(QtCore.QSize(0, 0))
        self.hiddenbutton.setText("")
        self.hiddenbutton.setObjectName("hiddenbutton")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap("src/hide.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.hiddenbutton.setIcon(icon2)
        self.hiddenbutton.clicked.connect(self.hiddenitems)

        self.horizontalLayout_3.addWidget(self.hiddenbutton)

        self.themebutton = QtWidgets.QPushButton(self.centralwidget)
        self.themebutton.setMinimumSize(QtCore.QSize(25, 25))
        self.themebutton.setMaximumSize(QtCore.QSize(25, 25))
        self.themebutton.setSizeIncrement(QtCore.QSize(0, 0))
        self.themebutton.setText("")
        self.themebutton.setObjectName("themebutton")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("src/sun-shape.svg"), QtGui.QIcon.Normal)
        self.themebutton.setIcon(icon)
        self.themebutton.clicked.connect(self.switchtheme)
        self.horizontalLayout_3.addWidget(self.themebutton)

        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.setCentralWidget(self.centralwidget)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self._createActions()
        self._createContextMenu()

        self.path_for_backButton_left = []
        self.path_for_backButton_right = []
        self.indexlist_left = []
        self.indexlist_right = []
        self.select_left = True
        self.select_right = True

        self.selected_left = []
        self.selected_right = []

        self.copylist = []

        self.cutchecking = False

        self.ignore_selection_changed_left = False
        self.ignore_selection_changed_right = False

        self.hiddenEnabled = False
        self.theme = 0

        self.rDirs = [
            "C:",
            "D:",
            "E:",
            "A:",
            "B:",
            "H:",
            "F:",
            "J:",
            "Q:",
            "Z:",
            "X:",
            "C:",
            "I:",
            "K:",
            "O:",
            "Y:",
        ]

    def contextMenuEvent(self, event):
        if self.listview_left.hasFocus():
            if self.pathbar_left.text() == "Drives":
                self.menu = QtWidgets.QMenu(self.listview_left)
                self.menu.addAction(self.hiddenAction)
                if (self.cutchecking) and (len(self.copylist) > 0):
                    self.menu.addAction(self.cancelAction)
                self.menu.popup(QCursor.pos())

            else:
                self.menu = QtWidgets.QMenu(self.listview_left)
                if not self.listview_left.selectionModel().hasSelection():
                    if len(self.copylist) > 0:
                        self.menu.addAction(self.pasteAction)
                    self.menu.addAction(self.NewFolderAction)
                    self.menu.addAction(self.hiddenAction)
                    if (self.cutchecking) and (len(self.copylist) > 0):
                        self.menu.addSeparator()
                        self.menu.addAction(self.cancelAction)
                elif self.listview_left.selectionModel().hasSelection():
                    self.menu.addAction(self.copyAction)
                    self.menu.addAction(self.delAction)
                    self.menu.addAction(self.cutAction)
                    self.menu.addAction(self.RenameAction)
                    if len(self.copylist) > 0:
                        self.menu.addAction(self.pasteAction)
                    self.menu.addSeparator()
                    self.menu.addAction(self.NewFolderAction)
                    self.menu.addAction(self.hiddenAction)
                    if (self.cutchecking) and (len(self.copylist) > 0):
                        self.menu.addSeparator()
                        self.menu.addAction(self.cancelAction)
                self.menu.popup(QCursor.pos())
        ######### treeview_left ############
        elif self.treeview_left.hasFocus():
            self.menu = QtWidgets.QMenu(self.treeview_left)
            if not self.treeview_left.selectionModel().hasSelection():
                self.menu.addAction(self.hiddenAction)
                if self.cutchecking:
                    self.menu.addSeparator()
                    self.menu.addAction(self.cancelAction)
            elif self.treeview_left.selectionModel().hasSelection():
                index = self.treeview_left.selectionModel().currentIndex()

                if self.dirModel_left.fileName(index)[-3:-1] in self.rDirs:
                    self.menu.addAction(self.hiddenAction)
                    if len(self.copylist) > 0:
                        self.menu.addAction(self.pasteAction)
                    if self.cutchecking:
                        self.menu.addSeparator()
                        self.menu.addAction(self.cancelAction)
                else:
                    self.menu.addAction(self.copyAction)
                    self.menu.addAction(self.RenameAction)
                    self.menu.addAction(self.cutAction)
                    self.menu.addAction(self.delAction)
                    self.menu.addSeparator()
                    self.menu.addAction(self.NewFolderAction)
                    self.menu.addAction(self.pasteAction)
                    if (self.cutchecking) and (len(self.copylist) > 0):
                        self.menu.addSeparator()
                        self.menu.addAction(self.cancelAction)
            self.menu.popup(QCursor.pos())
        elif self.listview_right.hasFocus():
            if self.pathbar_right.text() == "Drives":
                self.menu = QtWidgets.QMenu(self.listview_right)
                self.menu.addAction(self.hiddenAction)
                if (self.cutchecking) and (len(self.copylist) > 0):
                    self.menu.addAction(self.cancelAction)
                self.menu.popup(QCursor.pos())

            else:
                self.menu = QtWidgets.QMenu(self.listview_right)
                if not self.listview_right.selectionModel().hasSelection():
                    if len(self.copylist) > 0:
                        self.menu.addAction(self.pasteAction)
                    self.menu.addAction(self.NewFolderAction)
                    self.menu.addAction(self.hiddenAction)
                    if (self.cutchecking) and (len(self.copylist) > 0):
                        self.menu.addSeparator()
                        self.menu.addAction(self.cancelAction)
                elif self.listview_right.selectionModel().hasSelection():
                    self.menu.addAction(self.copyAction)
                    self.menu.addAction(self.delAction)
                    self.menu.addAction(self.cutAction)
                    self.menu.addAction(self.RenameAction)
                    if len(self.copylist) > 0:
                        self.menu.addAction(self.pasteAction)
                    self.menu.addSeparator()
                    self.menu.addAction(self.NewFolderAction)
                    self.menu.addAction(self.hiddenAction)
                    if (self.cutchecking) and (len(self.copylist) > 0):
                        self.menu.addSeparator()
                        self.menu.addAction(self.cancelAction)
                self.menu.popup(QCursor.pos())
        ######### treeview_left ############
        elif self.treeview_right.hasFocus():
            self.menu = QtWidgets.QMenu(self.treeview_right)
            if not self.treeview_right.selectionModel().hasSelection():
                self.menu.addAction(self.hiddenAction)
                if len(self.copylist) > 0:
                    self.menu.addAction(self.pasteAction)
                if (self.cutchecking) and (len(self.copylist) > 0):
                    self.menu.addSeparator()
                    self.menu.addAction(self.cancelAction)
            elif self.treeview_right.selectionModel().hasSelection():
                index = self.treeview_right.selectionModel().currentIndex()

                if self.dirModel_right.fileName(index)[-3:-1] in self.rDirs:
                    self.menu.addAction(self.hiddenAction)
                    if (self.cutchecking) and (len(self.copylist) > 0):
                        self.menu.addSeparator()
                        self.menu.addAction(self.cancelAction)
                else:
                    self.menu.addAction(self.copyAction)
                    self.menu.addAction(self.RenameAction)
                    self.menu.addAction(self.cutAction)
                    self.menu.addAction(self.delAction)
                    self.menu.addSeparator()
                    self.menu.addAction(self.NewFolderAction)
                    self.menu.addAction(self.pasteAction)
                    if (self.cutchecking) and (len(self.copylist) > 0):
                        self.menu.addSeparator()
                        self.menu.addAction(self.cancelAction)
            self.menu.popup(QCursor.pos())

    def _createContextMenu(self):
        ######### LEFT ############

        self.listview_left.addAction(self.RenameAction)
        self.listview_left.addAction(self.NewFolderAction)
        self.listview_left.addAction(self.delAction)
        self.listview_left.addAction(self.copyAction)
        self.listview_left.addAction(self.pasteAction)
        self.listview_left.addAction(self.cutAction)
        self.listview_left.addAction(self.cancelAction)
        self.listview_left.addAction(self.hiddenAction)

        self.treeview_left.addAction(self.cancelAction)

        self.treeview_left.addAction(self.delAction)
        self.treeview_left.addAction(self.RenameAction)
        self.treeview_left.addAction(self.NewFolderAction)
        self.treeview_left.addAction(self.cutAction)
        self.treeview_left.addAction(self.pasteAction)
        self.centralwidget.addAction(self.findAction)

        ######### RIGHT ############

        self.listview_right.addAction(self.RenameAction)
        self.listview_right.addAction(self.NewFolderAction)
        self.listview_right.addAction(self.delAction)
        self.listview_right.addAction(self.copyAction)
        self.listview_right.addAction(self.pasteAction)
        self.listview_right.addAction(self.cutAction)
        self.listview_right.addAction(self.cancelAction)
        self.listview_right.addAction(self.hiddenAction)
        self.listview_right.addAction(self.cancelAction)

        self.treeview_right.addAction(self.cancelAction)
        self.treeview_right.addAction(self.delAction)
        self.treeview_right.addAction(self.RenameAction)
        self.treeview_right.addAction(self.NewFolderAction)
        self.treeview_right.addAction(self.cutAction)
        self.treeview_right.addAction(self.pasteAction)
        self.centralwidget.addAction(self.findAction)

    def _createActions(self):
        self.RenameAction = QtWidgets.QAction(
            "Rename", triggered=self.renameItemPanelsAction
        )
        self.RenameAction.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F2))
        self.RenameAction.setShortcutVisibleInContextMenu(True)
        self.NewFolderAction = QtWidgets.QAction(
            "New Folder", triggered=self.newfolderPanelsAction
        )
        self.NewFolderAction.setShortcut(QtGui.QKeySequence("Ctrl+n"))
        self.delAction = QtWidgets.QAction("Delete", triggered=self.deleteFile)
        self.delAction.setShortcut(QtGui.QKeySequence("Del"))
        self.copyAction = QtWidgets.QAction("Copy", triggered=self.copyitems)
        self.copyAction.setShortcut(QtGui.QKeySequence("Ctrl+c"))
        self.pasteAction = QtWidgets.QAction(
            "Paste", triggered=self.pasteItemPanelsAction
        )
        self.pasteAction.setShortcut(QtGui.QKeySequence("Ctrl+v"))
        self.hiddenAction = QtWidgets.QAction(
            "show hidden Files", triggered=self.hiddenitems
        )
        self.hiddenAction.setCheckable(True)
        self.cutAction = QtWidgets.QAction("Cut file", triggered=self.cutfile)
        self.cutAction.setShortcut(QtGui.QKeySequence("Ctrl+x"))
        self.cancelAction = QtWidgets.QAction("Cancel cutting", triggered=self.cancel)
        self.findAction = QtWidgets.QAction("Find", triggered=self.openDialog_left)
        self.findAction.setShortcut(QtGui.QKeySequence("Ctrl+f"))

    def show_menu_left(self):
        self.menu_left = QtWidgets.QMenu(self.toolButton_left)
        self.actions_left = self.create_ToolBar_actions_left()
        self.menu_left.addActions(self.actions_left)
        self.toolButton_left.setMenu(self.menu_left)

        self.menu_left.exec_(
            self.toolButton_left.mapToGlobal(self.toolButton_left.rect().bottomLeft())
        )

    def show_menu_right(self):
        self.menu_right = QtWidgets.QMenu(self.toolButton_right)
        self.actions_right = self.create_ToolBar_actions_right()
        self.menu_right.addActions(self.actions_right)
        self.toolButton_right.setMenu(self.menu_right)

        self.menu_right.exec_(
            self.toolButton_right.mapToGlobal(self.toolButton_right.rect().bottomLeft())
        )

    def create_ToolBar_actions_left(self):
        action = QtWidgets.QAction("New Folder", triggered=self.newFolder_tool_left)
        action1 = QtWidgets.QAction("New File", triggered=self.newFolder_tool_right)
        if self.pathbar_left.text() == "Drives":
            action.setDisabled(True)
            action1.setDisabled(True)
        else:
            action.setEnabled(True)
            action1.setEnabled(True)

        return [action, action1]

    def create_ToolBar_actions_right(self):
        action = QtWidgets.QAction("New Folder", triggered=self.newFolder_tool_right)
        action1 = QtWidgets.QAction("New File", triggered=self.newFolder_tool_right)
        if self.pathbar_right.text() == "Drives":
            action.setDisabled(True)
            action1.setDisabled(True)
        else:
            action.setEnabled(True)
            action1.setEnabled(True)

        return [action, action1]

    def newFolder_tool_left(self):
        self.fileModel_left.setReadOnly(False)
        dest = os.path.abspath(self.pathbar_left.text() + "/New folder")
        if not os.path.exists(dest):
            os.mkdir(dest)
        ix = self.fileModel_left.index(dest)
        QtCore.QTimer.singleShot(
            0, lambda ix=ix: self.listview_left.setCurrentIndex(ix)
        )
        QtCore.QTimer.singleShot(0, lambda ix=ix: self.listview_left.edit(ix))
        ix = self.fileModel_left.index(os.path.abspath(self.pathbar_left.text()))
        self.listview_left.setCurrentIndex(ix)

    def newFolder_tool_right(self):
        self.fileModel_right.setReadOnly(False)
        dest = os.path.abspath(self.pathbar_right.text() + "/New folder")
        if not os.path.exists(dest):
            os.mkdir(dest)
        ix = self.fileModel_right.index(dest)
        QtCore.QTimer.singleShot(
            0, lambda ix=ix: self.listview_right.setCurrentIndex(ix)
        )
        QtCore.QTimer.singleShot(0, lambda ix=ix: self.listview_right.edit(ix))
        ix = self.fileModel_right.index(os.path.abspath(self.pathbar_right.text()))
        self.listview_right.setCurrentIndex(ix)

    def switchtheme(self):
        if self.theme == 0:
            self.setStyleSheet(mystylesheetlight(self))
            self.theme += 1

            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap("src/moon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off
            )

        elif self.theme == 1:
            self.setStyleSheet(mystylesheetdark(self))
            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap("src/sun-shape.svg"),
                QtGui.QIcon.Normal,
                QtGui.QIcon.Off,
            )
            self.theme = 0
        self.themebutton.setIcon(icon)

    def hiddenitems(self):
        if self.hiddenEnabled == False:
            self.fileModel_left.setFilter(
                QtCore.QDir.NoDotAndDotDot
                | QtCore.QDir.Hidden
                | QtCore.QDir.AllDirs
                | QtCore.QDir.Files
            )
            self.dirModel_left.setFilter(
                QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Hidden | QtCore.QDir.AllDirs
            )

            self.fileModel_right.setFilter(
                QtCore.QDir.NoDotAndDotDot
                | QtCore.QDir.Hidden
                | QtCore.QDir.AllDirs
                | QtCore.QDir.Files
            )
            self.dirModel_right.setFilter(
                QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Hidden | QtCore.QDir.AllDirs
            )

            self.hiddenEnabled = True
            self.hiddenAction.setChecked(True)

            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap("src/show.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off
            )

        else:
            self.fileModel_left.setFilter(
                QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs | QtCore.QDir.Files
            )
            self.dirModel_left.setFilter(
                QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs
            )

            self.fileModel_right.setFilter(
                QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs | QtCore.QDir.Files
            )
            self.dirModel_right.setFilter(
                QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs
            )

            self.hiddenEnabled = False
            self.hiddenAction.setChecked(False)
            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap("src/hide.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off
            )
        self.hiddenbutton.setIcon(icon)

    def openDialog_left(self, d):
        if not self.dialog_right.isVisible():
            self.dialog_left.pathbar_left.setText(
                self.pathbar_left.text() if self.pathbar_left.text() != "Drives" else ""
            )
            self.dialog_left.show()

    def openDialog_right(self, d):
        if not self.dialog_left.isVisible():
            self.dialog_right.pathbar_left.setText(
                self.pathbar_right.text()
                if self.pathbar_right.text() != "Drives"
                else ""
            )
            self.dialog_right.show()

    def handlePathEntered_left(self, path):
        self.select_left = False
        self.path_for_backButton_left.append(
            "" if self.pathbar_left.text() == "Drives" else self.pathbar_left.text()
        )

        if path.upper() in self.rDirs:
            path += "/"

        if not os.path.isdir(path):
            if path == "":
                self.listview_left.setRootIndex(self.fileModel_left.index(""))
                self.pathbar_left.setText("Drives")
                return
            else:
                os.startfile(str(path))
                path = os.path.dirname(path) if len(path) > 3 else ""
                self.listview_left.setRootIndex(self.fileModel_left.setRootPath(path))
                self.listview_left.setCurrentIndex(self.fileModel_left.index(path))
                self.treeview_left.setCurrentIndex(self.dirModel_left.index(path[:3]))

        else:
            self.treeview_left.setCurrentIndex(
                self.dirModel_left.index(os.path.abspath(path)[:3])
            )
            self.listview_left.setRootIndex(
                self.fileModel_left.setRootPath(os.path.abspath(path))
            )

        self.pathbar_dest_left(os.path.abspath(path))

    def handlePathEntered_right(self, path):
        self.select_right = False
        self.path_for_backButton_right.append(
            "" if self.pathbar_right.text() == "Drives" else self.pathbar_right.text()
        )

        if path.upper() in self.rDirs:
            path += "/"

        if not os.path.isdir(path):
            if path == "":
                self.listview_right.setRootIndex(self.fileModel_right.index(""))
                self.pathbar_right.setText("Drives")
                return
            else:
                os.startfile(str(path))
                path = os.path.dirname(path) if len(path) > 3 else ""
                self.listview_right.setRootIndex(self.fileModel_right.setRootPath(path))
                self.listview_right.setCurrentIndex(self.fileModel_right.index(path))
                self.treeview_right.setCurrentIndex(self.dirModel_right.index(path[:3]))

        else:
            self.treeview_right.setCurrentIndex(
                self.dirModel_right.index(os.path.abspath(path)[:3])
            )
            self.listview_right.setRootIndex(
                self.fileModel_right.setRootPath(os.path.abspath(path))
            )

        self.pathbar_dest_right(os.path.abspath(path))

    def copyitems(self):
        self.copylist = []
        self.indexlist_left = []
        self.indexlist_right = []
        if self.listview_right.hasFocus():
            self.selected_right = self.listview_right.selectionModel().selectedRows()

            if self.cutchecking:
                self.delegate_right = StyledItemDelegate(indexes=self.selected_right)
                self.listview_right.setItemDelegate(self.delegate_right)

            for index in self.selected_right:
                path = os.path.abspath(
                    self.pathbar_right.text()
                    + "/"
                    + self.fileModel_right.data(
                        index, self.fileModel_right.FileNameRole
                    )
                )
                self.copylist.append(path)
                self.indexlist_right.append(index)

        elif self.treeview_right.hasFocus():
            self.selected_right = self.treeview_right.selectionModel().selectedRows()

            if self.cutchecking:
                self.delegate_right = StyledItemDelegate(indexes=self.selected_right)
                self.treeview_right.setItemDelegate(self.delegate_right)

            for index in self.selected_right:
                path = os.path.abspath(self.pathbar_right.text())
                self.copylist.append(path)
                self.indexlist_right.append(index)

        elif self.listview_left.hasFocus():
            self.selected_left = self.listview_left.selectionModel().selectedRows()

            if self.cutchecking:
                self.delegate_left = StyledItemDelegate(indexes=self.selected_left)
                self.listview_left.setItemDelegate(self.delegate_left)

            for index in self.selected_left:
                path = os.path.abspath(
                    self.pathbar_left.text()
                    + "/"
                    + self.fileModel_left.data(index, self.fileModel_left.FileNameRole)
                )
                self.copylist.append(path)
                self.indexlist_left.append(index)

        elif self.treeview_left.hasFocus():
            self.selected_left = self.treeview_left.selectionModel().selectedRows()

            if self.cutchecking:
                self.delegate_left = StyledItemDelegate(indexes=self.selected_left)
                self.treeview_left.setItemDelegate(self.delegate_left)

            for index in self.selected_left:
                path = os.path.abspath(self.pathbar_left.text())
                self.copylist.append(path)
                self.indexlist_left.append(index)

    def pasteItemPanelsAction(self):
        chech = []
        text = (
            "Вы желаете вставить элемент?"
            if len(self.copylist) == 1
            else "Вы желаете вставить элементы?"
        )
        self.destTarg = []
        if self.listview_left.hasFocus():
            chech.append(
                os.path.abspath(
                    self.fileModel_left.filePath(
                        self.listview_left.selectionModel().currentIndex()
                    )
                )
            )
            if self.cutchecking == True and (chech[0] in self.copylist):
                Errors.cutIn(self)
                return

            msg = QMessageBox.question(
                self,
                "Pasting file",
                text,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if msg == QMessageBox.Yes:
                for target in self.copylist:
                    if self.listview_left.selectionModel().hasSelection():
                        destpath = self.fileModel_left.filePath(
                            self.listview_left.selectionModel().currentIndex()
                        )
                    else:
                        destpath = self.pathbar_left.text()

                    destination = os.path.abspath(
                        os.path.abspath(destpath)
                        + "/"
                        + QtCore.QFileInfo(target).fileName()
                    )
                    if os.path.exists(destination):
                        if os.path.isdir(target):
                            destination = self.checkforExist(destination + "_1")
                        else:
                            destination = self.checkforExist_app(destination)

                    self.destTarg.append(target)
                    self.destTarg.append(destination)

        elif self.treeview_left.hasFocus():
            chech.append(
                os.path.abspath(
                    self.dirModel_left.filePath(
                        self.treeview_left.selectionModel().currentIndex()
                    )
                )
            )
            if self.cutchecking == True and (chech[0] in self.copylist):
                Errors.cutIn(self)
                return

            msg = QMessageBox.question(
                self,
                "Pasting file",
                text,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if msg == QMessageBox.Yes:
                for target in self.copylist:
                    destination = os.path.abspath(
                        self.pathbar_left.text()
                        + "/"
                        + QtCore.QFileInfo(target).fileName()
                    )
                    if os.path.exists(destination):
                        if os.path.isdir(target):
                            destination = self.checkforExist(destination + "_1")
                        else:
                            destination = self.checkforExist_app(destination)
                    self.destTarg.append(target)
                    self.destTarg.append(destination)

        elif self.listview_right.hasFocus():
            chech.append(
                os.path.abspath(
                    self.fileModel_right.filePath(
                        self.listview_right.selectionModel().currentIndex()
                    )
                )
            )
            if self.cutchecking == True and (chech[0] in self.copylist):
                Errors.cutIn(self)
                return

            msg = QMessageBox.question(
                self,
                "Pasting file",
                text,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if msg == QMessageBox.Yes:
                for target in self.copylist:
                    if self.listview_right.selectionModel().hasSelection():
                        destpath = self.fileModel_right.filePath(
                            self.listview_right.selectionModel().currentIndex()
                        )
                    else:
                        destpath = self.pathbar_right.text()
                    destination = os.path.abspath(
                        os.path.abspath(destpath)
                        + "/"
                        + QtCore.QFileInfo(target).fileName()
                    )
                    if os.path.exists(destination):
                        if os.path.isdir(target):
                            destination = self.checkforExist(destination + "_1")
                        else:
                            destination = self.checkforExist_app(destination)
                    self.destTarg.append(target)
                    self.destTarg.append(destination)

        elif self.treeview_right.hasFocus():
            chech.append(
                os.path.abspath(
                    self.dirModel_right.filePath(
                        self.treeview_right.selectionModel().currentIndex()
                    )
                )
            )
            if self.cutchecking == True and (chech[0] in self.copylist):
                Errors.cutIn(self)
                return

            msg = QMessageBox.question(
                self,
                "Pasting file",
                text,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if msg == QMessageBox.Yes:
                for target in self.copylist:
                    destination = os.path.abspath(
                        self.pathbar_right.text()
                        + "/"
                        + QtCore.QFileInfo(target).fileName()
                    )
                    if os.path.exists(destination):
                        if os.path.isdir(target):
                            destination = self.checkforExist(destination + "_1")
                        else:
                            destination = self.checkforExist_app(destination)
                    self.destTarg.append(target)
                    self.destTarg.append(destination)

        if msg == QMessageBox.Yes:
            progress_dialog = ProgressDialog_Paste(self.destTarg)
            progress_dialog.start_pasting()
            progress_dialog.exec_()

            if self.cutchecking:
                for index in self.indexlist_left:
                    self.fileModel_left.remove(index)
                for index in self.indexlist_right:
                    self.fileModel_right.remove(index)
                self.copylist = []
                self.cutchecking = False

    def renameItemPanelsAction(self):
        if self.listview_left.hasFocus():
            self.fileModel_left.setReadOnly(False)
            d = os.path.abspath(
                self.fileModel_left.filePath(
                    self.listview_left.selectionModel().currentIndex()
                )
            )
            ix = self.fileModel_left.index(d)
            QtCore.QTimer.singleShot(
                0, lambda ix=ix: self.listview_left.setCurrentIndex(ix)
            )
            QtCore.QTimer.singleShot(0, lambda ix=ix: self.listview_left.edit(ix))
        elif self.treeview_left.hasFocus():
            try:
                if self.listview_left.hasFocus():
                    self.fileModel_left.setReadOnly(False)
                    dest = os.path.abspath(self.pathbar_left.text() + "/New folder")
                    if not os.path.exists(dest):
                        os.mkdir(dest)
                    ix = self.fileModel_left.index(dest)
                    QtCore.QTimer.singleShot(
                        0, lambda ix=ix: self.listview_left.setCurrentIndex(ix)
                    )
                    QtCore.QTimer.singleShot(
                        0, lambda ix=ix: self.listview_left.edit(ix)
                    )
                    ix = self.fileModel_left.index(
                        os.path.abspath(self.pathbar_left.text())
                    )
                    self.listview_left.setCurrentIndex(ix)
                elif self.treeview_left.hasFocus():
                    try:
                        self.dirModel_left.setReadOnly(False)
                        dest = os.path.abspath(self.pathbar_left.text() + "/New folder")
                        if not os.path.exists(dest):
                            os.mkdir(dest)
                        ix = self.dirModel_left.index(dest)
                        QtCore.QTimer.singleShot(
                            0, lambda ix=ix: self.treeview_left.edit(ix)
                        )
                        ix = self.dirModel_left.index(
                            os.path.abspath(self.pathbar_left.text())
                        )
                        self.treeview_left.setCurrentIndex(ix)
                    except:
                        pass
            except:
                pass
        elif self.listview_right.hasFocus():
            self.fileModel_right.setReadOnly(False)
            d = os.path.abspath(
                self.fileModel_right.filePath(
                    self.listview_right.selectionModel().currentIndex()
                )
            )
            ix = self.fileModel_right.index(d)
            QtCore.QTimer.singleShot(
                0, lambda ix=ix: self.listview_right.setCurrentIndex(ix)
            )
            QtCore.QTimer.singleShot(0, lambda ix=ix: self.listview_right.edit(ix))
        elif self.treeview_right.hasFocus():
            try:
                if self.listview_right.hasFocus():
                    self.fileModel_right.setReadOnly(False)
                    dest = os.path.abspath(self.pathbar_right.text() + "/New folder")
                    if not os.path.exists(dest):
                        os.mkdir(dest)
                    ix = self.fileModel_right.index(dest)
                    QtCore.QTimer.singleShot(
                        0, lambda ix=ix: self.listview_right.setCurrentIndex(ix)
                    )
                    QtCore.QTimer.singleShot(
                        0, lambda ix=ix: self.listview_right.edit(ix)
                    )
                    ix = self.fileModel_right.index(
                        os.path.abspath(self.pathbar_right.text())
                    )
                    self.listview_right.setCurrentIndex(ix)
                elif self.treeview_right.hasFocus():
                    try:
                        self.dirModel_right.setReadOnly(False)
                        dest = os.path.abspath(
                            self.pathbar_right.text() + "/New folder"
                        )
                        if not os.path.exists(dest):
                            os.mkdir(dest)
                        ix = self.dirModel_right.index(dest)
                        QtCore.QTimer.singleShot(
                            0, lambda ix=ix: self.treeview_right.edit(ix)
                        )
                        ix = self.dirModel_right.index(
                            os.path.abspath(self.pathbar_right.text())
                        )
                        self.treeview_right.setCurrentIndex(ix)
                    except:
                        pass
            except:
                pass

    def newfolderPanelsAction(self):
        try:
            if self.listview_left.hasFocus():
                self.fileModel_left.setReadOnly(False)
                dest = os.path.abspath(self.pathbar_left.text() + "/New folder")
                if not os.path.exists(dest):
                    os.mkdir(dest)
                else:
                    dest = self.checkforExist(dest + "_1")
                    os.mkdir(dest)
                ix = self.fileModel_left.index(dest)
                QtCore.QTimer.singleShot(
                    0, lambda ix=ix: self.listview_left.setCurrentIndex(ix)
                )
                QtCore.QTimer.singleShot(0, lambda ix=ix: self.listview_left.edit(ix))
                ix = self.fileModel_left.index(
                    os.path.abspath(self.pathbar_left.text())
                )
                self.listview_left.setCurrentIndex(ix)
            elif self.treeview_left.hasFocus():
                try:
                    self.dirModel_left.setReadOnly(False)
                    dest = os.path.abspath(self.pathbar_left.text() + "/New folder")
                    if not os.path.exists(dest):
                        os.mkdir(dest)
                    else:
                        dest = self.checkforExist(dest + "_1")
                        os.mkdir(dest)
                    ix = self.dirModel_left.index(dest)
                    QtCore.QTimer.singleShot(
                        0, lambda ix=ix: self.treeview_left.edit(ix)
                    )
                    ix = self.dirModel_left.index(
                        os.path.abspath(self.pathbar_left.text())
                    )
                    self.treeview_left.setCurrentIndex(ix)
                except:
                    pass
            elif self.listview_right.hasFocus():
                self.fileModel_right.setReadOnly(False)
                dest = os.path.abspath(self.pathbar_right.text() + "/New folder")
                if not os.path.exists(dest):
                    os.mkdir(dest)
                else:
                    dest = self.checkforExist(dest + "_1")
                    os.mkdir(dest)
                ix = self.fileModel_right.index(dest)
                QtCore.QTimer.singleShot(
                    0, lambda ix=ix: self.listview_right.setCurrentIndex(ix)
                )
                QtCore.QTimer.singleShot(0, lambda ix=ix: self.listview_right.edit(ix))
                ix = self.fileModel_right.index(
                    os.path.abspath(self.pathbar_right.text())
                )
                self.listview_right.setCurrentIndex(ix)
            elif self.treeview_right.hasFocus():
                try:
                    self.dirModel_right.setReadOnly(False)
                    dest = os.path.abspath(self.pathbar_right.text() + "/New folder")
                    if not os.path.exists(dest):
                        os.mkdir(dest)
                    else:
                        dest = self.checkforExist(dest + "_1")
                        os.mkdir(dest)
                    ix = self.dirModel_right.index(dest)
                    QtCore.QTimer.singleShot(
                        0, lambda ix=ix: self.treeview_right.edit(ix)
                    )
                    ix = self.dirModel_right.index(
                        os.path.abspath(self.pathbar_right.text())
                    )
                    self.treeview_right.setCurrentIndex(ix)
                except:
                    pass
        except:
            pass

    def cancel(self):
        self.delegate_left = StyledItemDelegate_cancel(indexes=self.selected_left)
        self.listview_left.setItemDelegate(self.delegate_left)
        self.treeview_left.setItemDelegate(self.delegate_left)

        self.delegate_right = StyledItemDelegate_cancel(indexes=self.selected_right)
        self.listview_right.setItemDelegate(self.delegate_right)
        self.treeview_right.setItemDelegate(self.delegate_right)

        self.cutchecking = False
        self.copylist = []

    def cutfile(self):
        self.cancel()
        self.cutchecking = True
        self.copyitems()

    def deleteFile(self):
        msg = QMessageBox.question(
            self,
            "Deleting file",
            f"""Вы желаете удалить элемент?""",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if msg == QMessageBox.Yes:
            if self.listview_left.hasFocus():
                index = self.listview_left.selectionModel().selectedIndexes()
                for delFile in self.listview_left.selectionModel().selectedIndexes():
                    path = os.path.abspath(
                        self.fileModel_left.fileInfo(delFile).absoluteFilePath()
                    )

                    if path in self.copylist:
                        self.copylist.remove(path)

                progress_dialog = ProgressDialog(self.fileModel_left, index)
                progress_dialog.start_deletion()
                progress_dialog.exec_()

            elif self.treeview_left.hasFocus():
                index = self.treeview_left.selectionModel().selectedIndexes()
                path = os.path.abspath(self.pathbar_left.text())
                if path in self.copylist:
                    self.copylist.remove(path)

                progress_dialog = ProgressDialog(self.dirModel_left, index)
                progress_dialog.start_deletion()
                progress_dialog.exec_()

            elif self.listview_right.hasFocus():
                index = self.listview_right.selectionModel().selectedIndexes()
                for delFile in self.listview_right.selectionModel().selectedIndexes():
                    path = os.path.abspath(
                        self.fileModel_right.fileInfo(delFile).absoluteFilePath()
                    )

                    if path in self.copylist:
                        self.copylist.remove(path)

                progress_dialog = ProgressDialog(self.fileModel_right, index)
                progress_dialog.start_deletion()
                progress_dialog.exec_()

            elif self.treeview_right.hasFocus():
                index = self.treeview_right.selectionModel().selectedIndexes()
                path = os.path.abspath(self.pathbar_right.text())

                if path in self.copylist:
                    self.copylist.remove(path)

                progress_dialog = ProgressDialog(self.dirModel_right, index)
                progress_dialog.start_deletion()
                progress_dialog.exec_()

    def goUp_click_left(self):
        self.listview_left.clearSelection()
        self.listview_left.collapseAll()

        newpath = (
            os.path.dirname(self.pathbar_left.text())
            if len(self.pathbar_left.text()) > 3
            else ""
        )

        self.listview_left.setRootIndex(self.fileModel_left.setRootPath(newpath))

        self.path_for_backButton_left.append(
            "" if self.pathbar_left.text() == "Drives" else self.pathbar_left.text()
        )
        self.row_for_back_left(newpath)

    def goUp_click_right(self):
        self.listview_right.clearSelection()
        self.listview_right.collapseAll()

        newpath = (
            os.path.dirname(self.pathbar_right.text())
            if len(self.pathbar_right.text()) > 3
            else ""
        )

        self.listview_right.setRootIndex(self.fileModel_right.setRootPath(newpath))

        self.path_for_backButton_right.append(
            "" if self.pathbar_right.text() == "Drives" else self.pathbar_right.text()
        )
        self.row_for_back_right(newpath)

    def back_click_left(self):
        self.listview_left.collapseAll()
        self.list_clear_left()
        print(self.path_for_backButton_left)

        try:
            backup = self.path_for_backButton_left.pop()
            self.listview_left.setRootIndex(self.fileModel_left.index(backup))
            self.row_for_back_left(backup + "/" if len(backup) == 2 else backup)

        except:
            self.listview_left.setRootIndex(self.fileModel_left.index(""))
            self.row_for_back_left("")
        self.listview_left.clearSelection()

    def back_click_right(self):
        self.listview_right.collapseAll()
        self.list_clear_right()

        try:
            backup = self.path_for_backButton_right.pop()
            self.listview_right.setRootIndex(self.fileModel_right.index(backup))
            self.row_for_back_right(backup + "/" if len(backup) == 2 else backup)

        except:
            self.listview_right.setRootIndex(self.fileModel_right.index(""))
            self.row_for_back_right("")
        self.listview_right.clearSelection()

    def list_clear_left(self):
        for i in range(len(self.path_for_backButton_left)):
            try:
                if (
                    self.path_for_backButton_left[i]
                    == self.path_for_backButton_left[i + 1]
                ):
                    self.path_for_backButton_left.remove(
                        self.path_for_backButton_left[i]
                    )

            except:
                pass

    def list_clear_right(self):
        for i in range(len(self.path_for_backButton_right)):
            try:
                if (
                    self.path_for_backButton_right[i]
                    == self.path_for_backButton_right[i + 1]
                ):
                    self.path_for_backButton_right.remove(
                        self.path_for_backButton_right[i]
                    )

            except:
                pass

    def tree_doubleClicked_left(self):
        index = self.treeview_left.selectionModel().currentIndex()
        path = self.dirModel_left.fileInfo(index).absoluteFilePath()

        if not self.dirModel_left.fileInfo(index).isDir():
            os.startfile(str(path))
        else:
            self.listview_left.setRootIndex(self.fileModel_left.setRootPath(path))

    def tree_doubleClicked_right(self):
        index = self.treeview_right.selectionModel().currentIndex()
        path = self.dirModel_right.fileInfo(index).absoluteFilePath()

        if not self.dirModel_right.fileInfo(index).isDir():
            os.startfile(str(path))
        else:
            self.listview_right.setRootIndex(self.fileModel_right.setRootPath(path))

    def on_selectionChanged_left(self):
        if self.ignore_selection_changed_left:
            return

        index = self.treeview_left.selectionModel().currentIndex()
        path = self.dirModel_left.fileInfo(index).absoluteFilePath()
        self.listview_left.setRootIndex(self.fileModel_left.setRootPath(path))
        if not self.dirModel_left.fileInfo(index).isDir():
            pass
        self.listview_left.clearFocus()
        self.listview_left.clearSelection()

        if self.select_left:
            self.path_for_backButton_left.append(
                "" if self.pathbar_left.text() == "Drives" else self.pathbar_left.text()
            )

        else:
            self.select_left = True

        self.getRowCount_tree_left()

    def on_selectionChanged_right(self):
        if self.ignore_selection_changed_right:
            return

        index = self.treeview_right.selectionModel().currentIndex()
        path = self.dirModel_right.fileInfo(index).absoluteFilePath()
        self.listview_right.setRootIndex(self.fileModel_right.setRootPath(path))
        if not self.dirModel_right.fileInfo(index).isDir():
            pass
        self.listview_right.clearFocus()
        self.listview_right.clearSelection()

        if self.select_right:
            self.path_for_backButton_right.append(
                ""
                if self.pathbar_right.text() == "Drives"
                else self.pathbar_right.text()
            )

        else:
            self.select_right = True

        self.getRowCount_tree_right()

    def list_doubleClicked_left(self):
        self.fileModel_left.setReadOnly(True)

        index = self.listview_left.selectionModel().currentIndex()
        path = self.fileModel_left.fileInfo(index).absoluteFilePath()

        if not self.fileModel_left.fileInfo(index).isDir():
            os.startfile(os.path.abspath(path))
        else:
            self.path_for_backButton_left.append(
                "" if self.pathbar_left.text() == "Drives" else self.pathbar_left.text()
            )
            self.treeview_left.setCurrentIndex(self.dirModel_left.index(path[:3]))
            self.listview_left.setRootIndex(self.fileModel_left.setRootPath(path))
            self.getRowCount_left()

    def list_doubleClicked_right(self):
        self.fileModel_right.setReadOnly(True)

        index = self.listview_right.selectionModel().currentIndex()
        path = self.fileModel_right.fileInfo(index).absoluteFilePath()

        if not self.fileModel_right.fileInfo(index).isDir():
            os.startfile(os.path.abspath(path))
        else:
            self.path_for_backButton_right.append(
                ""
                if self.pathbar_right.text() == "Drives"
                else self.pathbar_right.text()
            )
            self.treeview_right.setCurrentIndex(self.dirModel_right.index(path[:3]))
            self.listview_right.setRootIndex(self.fileModel_right.setRootPath(path))
            self.getRowCount_right()

    def getRowCount_tree_left(self):
        index = self.treeview_left.selectionModel().currentIndex()
        path1 = QtCore.QDir(self.dirModel_left.fileInfo(index).absoluteFilePath())
        count = len(path1.entryList(QtCore.QDir.Files))

        index_for_checker = self.treeview_left.selectionModel().currentIndex()
        check = self.dirModel_left.fileInfo(index_for_checker).absoluteFilePath()

        self.statusbar.showMessage(f"{count} files", 0)

        self.pathbar_dest_left(check)

        return count

    def getRowCount_tree_right(self):
        index = self.treeview_right.selectionModel().currentIndex()
        path1 = QtCore.QDir(self.dirModel_right.fileInfo(index).absoluteFilePath())
        count = len(path1.entryList(QtCore.QDir.Files))

        index_for_checker = self.treeview_right.selectionModel().currentIndex()
        check = self.dirModel_left.fileInfo(index_for_checker).absoluteFilePath()

        self.statusbar.showMessage(f"{count} files", 0)

        self.pathbar_dest_right(check)

        return count

    def getRowCount_left(self):
        index = self.listview_left.selectionModel().currentIndex()
        path = QtCore.QDir(self.fileModel_left.fileInfo(index).absoluteFilePath())
        count = len(path.entryList(QtCore.QDir.Files))

        index_for_checker = self.listview_left.selectionModel().currentIndex()
        check = self.fileModel_left.fileInfo(index_for_checker).absoluteFilePath()

        if check == "":
            count = 0

        self.statusbar.showMessage(f"{count} files", 0)

        self.pathbar_dest_left(check)

        return count

    def getRowCount_right(self):
        index = self.listview_right.selectionModel().currentIndex()
        path = QtCore.QDir(self.fileModel_right.fileInfo(index).absoluteFilePath())
        count = len(path.entryList(QtCore.QDir.Files))

        index_for_checker = self.listview_right.selectionModel().currentIndex()
        check = self.fileModel_right.fileInfo(index_for_checker).absoluteFilePath()

        if check == "":
            count = 0

        self.statusbar.showMessage(f"{count} files", 0)

        self.pathbar_dest_right(check)

        return count

    def row_for_back_left(self, path):
        path_checker = QtCore.QDir(path)
        count = len(path_checker.entryList(QtCore.QDir.Files))

        if path == "":
            count = 0

        self.statusbar.showMessage(f"{count} files", 0)

        self.pathbar_dest_left(path)

        return count

    def row_for_back_right(self, path):
        path_checker = QtCore.QDir(path)
        count = len(path_checker.entryList(QtCore.QDir.Files))

        if path == "":
            count = 0

        self.statusbar.showMessage(f"{count} files", 0)

        self.pathbar_dest_right(path)

        return count

    def pathbar_dest_left(self, path):
        self.pathbar_left.setText(os.path.abspath(path) if path != "" else "Drives")
        self.dialog_left.pathbar_left.setText(
            os.path.abspath(path) if path != "" else "Drives"
        )
        if self.pathbar_left.text() == "Drives":
            self.clear_treeview_selection_left()

    def pathbar_dest_right(self, path):
        self.pathbar_right.setText(os.path.abspath(path) if path != "" else "Drives")
        self.dialog_left.pathbar_left.setText(
            os.path.abspath(path) if path != "" else "Drives"
        )
        if self.pathbar_right.text() == "Drives":
            self.clear_treeview_selection_right()

    def clear_treeview_selection_left(self):
        self.ignore_selection_changed_left = True
        self.treeview_left.clearSelection()
        self.ignore_selection_changed_left = False

    def clear_treeview_selection_right(self):
        self.ignore_selection_changed_right = True
        self.treeview_right.clearSelection()
        self.ignore_selection_changed_right = False

    def checkforExist(self, dest):
        if os.path.exists(dest):
            dest = dest[:-1] + f"{int(dest[-1]) + 1}"
            return self.checkforExist(dest)
        else:
            return dest

    def checkforExist_app(self, dest):
        i = len(dest) - 1
        while i:
            if dest[i] == ".":
                break
            i -= 1
        dest = self.checkforExist_appType(dest[:i] + "_1", dest[i:])
        return dest

    def checkforExist_appType(self, dest, type):
        if os.path.exists(dest + type):
            dest = dest[:-1] + f"{int(dest[-1]) + 1}"
            return self.checkforExist_appType(dest, type)
        else:
            return dest + type


def mystylesheetdark(self):
    return """

QWidget{
    background-color: grey;
}

QTreeView{
    border:none;
    background-color: darkgrey;
    border-radius: 10px;
    show-decoration-selected: 0;
    outline: 0;
    selection-background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #FFC618, stop: 1  #204a87);
    padding-bottom: 5px;
}
QTreeView::item{
height: 25px;
color: black;
font-weight: 600;
}

QTreeView::item:!selected:hover {
    background: #a1a1a1;
}

QTreeView::item:selected:!hover{
    background: #8f8f8f;
}

QTreeView::item:selected:hover{
    border: 0px;
    background: #9e9e9e;
}
QTreeView::item::focus{
    color: black;
    border: 0px;
}

QTreeView::focus{
    border-style: solid;
    border-color: darkgrey; 
    border-width: 1px;

    color: black;
}

QTreeView::focus{
    border:1px solid black/;
    
}

QHeaderView::section{
    font-size: 13px;
    font-weight: 500;
}

QPushButton{
border-style: solid;
border-color: darkgrey;
background-color: #b6b6b6;
font-size: 8pt;
border-width: 1px;
border-radius: 6px;
border: none;
min-width: 25px;
}
QPushButton:hover:!pressed{
border-style: solid;
border-color: darkgrey;
border-width: 1px;
border-radius: 6px;
padding: 4px;
}
QPushButton:hover{
background-color: white;
border-style: solid;
border-color: darkgrey;
border-width: 1px;
border-radius: 6px;
}

QLineEdit{
    border-style: solid;
    border-color: darkgrey;
    border-radius: 6px;
    background-color: #333;
    color: #c2c2c2;
    font-weight: bold;
    padding: 5px;
}

QSplitter {
    width: 8px;
}
QScrollBar
{
background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #9c9c9c, stop: 1  #848484)
}
QMenu
{
background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
}
QMenu
{
background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
}
QMenu::item::selected
{
background: grey;
}

QMessageBox
{
    font-size: 16px;
    text-align: center;
    color: white;
}

QMessageBox QPushButton
{
    min-width: 70px;
    min-height: 25px;
}
QMessageBox QLabel#qt_msgbox_label {
    color: white;
    background-color: dark;
    min-width: 350px;
    min-height: 40px;
}

    """


def mystylesheetlight(self):
    return """

    QWidget{
        background-color: #dce0dd;
    }

    QTreeView{
        border:none;
        background-color: #ffffff;
        border-radius: 10px;
        show-decoration-selected: 0;
        outline: 0;
        selection-background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #729fcf, stop: 1  #204a87);
    }
    QTreeView::item{
    height: 25px;
    color: black;
font-weight: 600;

    }   

    QTreeView::item:!selected:hover {
        background: #ededed;
    }

    QTreeView::item:selected:!hover{
        background: #ededed;
    }

    QTreeView::item:selected:hover{
        border: 0px;
        background: #ededed;
    }
    QTreeView::item::focus{
        color: black;
        border: 0px;
    }



    QHeaderView::section{
        font-size: 13px;
        font-weight: 500;
    }

    QPushButton{
    border-style: solid;
    border-color: darkgrey;
    background-color: #ffffff;
    font-size: 8pt;
    border-width: 1px;
    border-radius: 6px;
    border: none;
    min-width: 25px;
    
    }
    QPushButton:hover:!pressed{
    border-style: solid;
    border-color: darkgrey;
    border-width: 1px;
    border-radius: 6px;
    padding: 4px;
    }
    QPushButton:hover{
    background-color: white;
    border-style: solid;
    border-color: darkgrey;
    border-width: 1px;
    border-radius: 6px;
    }

    QLineEdit{
        border-style: solid;
        border-color: darkgrey;
        border-radius: 6px;
        background-color: white;
        color: dark;
        font-weight: bold;
        padding: 5px;
    }

    QSplitter {
        width: 8px;
    }

    QScrollBar
    {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #9c9c9c, stop: 1  #848484)
    }
    QMenu
    {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                    stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
    }
    QMenu
    {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                    stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
    }
    QMenu::item::selected
    {
    background: grey;
    }
    QMessageBox
{
    font-size: 16px;
    text-align: center;
    color: white;
}

QMessageBox QPushButton
{
    min-width: 70px;
    min-height: 25px;
}
QMessageBox QLabel#qt_msgbox_label {
    color: white;
    background-color: transparent;
    min-width: 350px;
    min-height: 40px;
}
        """


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    MainWindow = Window()
    MainWindow.show()

    MainWindow.setWindowTitle("FileManager")
    sys.exit(app.exec_())
