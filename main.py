from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, QItemSelectionModel
from threading import Thread
import os
import sys
import subprocess
import shutil
import errno


class ClssDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ClssDialog, self).__init__(parent)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.closebutton = QtWidgets.QPushButton(self)
        self.closebutton.setObjectName("pushButton")
        # self.closebutton.clicked.connect(self.btnClosed)
        self.verticalLayout.addWidget(self.closebutton)
        self.setWindowTitle("Dialog")
        self.closebutton.setText("Close Dialog")

    # def btnClosed(self):
    #     self.close()


class MyLineEdit(QtWidgets.QLineEdit):
    def focusInEvent(self, e):
        try:
            self.CallBack(*self.CallBackArgs)
        except AttributeError:
            pass
        super().focusInEvent(e)

    def SetCallBack(self, callBack):
        self.CallBack = callBack
        self.IsCallBack = True
        self.CallBackArgs = []

    def SetCallBackArgs(self, args):
        self.CallBackArgs = args


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setObjectName("MainWindow")
        self.resize(800, 600)

        self.setStyleSheet(mystylesheetdark(self))

        self.hiddenEnabled = False
        # self.clip = QtWidgets.QApplication.clipboard()
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.verticalalignallprogram = QtWidgets.QVBoxLayout()
        self.verticalalignallprogram.setObjectName("verticalalignallprogram")

        self.horizontalshapka = QtWidgets.QHBoxLayout()
        self.horizontalshapka.setObjectName("horizontalshapka")

        self.backbutton = QtWidgets.QPushButton(self.centralwidget)
        self.backbutton.setMaximumSize(QtCore.QSize(100, 100))
        self.backbutton.setMinimumSize(QtCore.QSize(25, 25))
        self.backbutton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("arrows/left-arrow.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )

        self.backbutton.setIcon(icon)
        self.backbutton.setObjectName("backbutton")
        self.backbutton.clicked.connect(self.back_click)

        self.horizontalshapka.addWidget(self.backbutton)

        self.upbutton = QtWidgets.QPushButton(self.centralwidget)
        self.upbutton.setMaximumSize(QtCore.QSize(100, 100))
        self.upbutton.setMinimumSize(QtCore.QSize(25, 25))
        self.upbutton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap("arrows/up-arrow.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.upbutton.setIcon(icon1)
        self.upbutton.setObjectName("upbutton")
        self.horizontalshapka.addWidget(self.upbutton)

        self.upbutton.clicked.connect(self.goUp_click)

        # self.pathbar = QtWidgets.QLineEdit(self.centralwidget)
        self.pathbar = MyLineEdit()
        self.pathbar.setMinimumSize(QtCore.QSize(20, 20))
        self.pathbar.setObjectName("pathbar")
        # self.pathbar.SetCallBack(self.openDialog)
        self.horizontalshapka.addWidget(self.pathbar)

        # print(self.pathbar.)

        self.verticalalignallprogram.addLayout(self.horizontalshapka)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.treeview = QtWidgets.QTreeView(self.centralwidget)
        self.treeview.setMaximumSize(QtCore.QSize(250, 16777215))
        self.treeview.setObjectName("treeview")

        self.listview = QtWidgets.QTreeView(self.centralwidget)
        self.listview.setObjectName("listview")

        self.verticalalignallprogram.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalalignallprogram, 1, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.horizontalfooter = QtWidgets.QHBoxLayout()
        self.horizontalfooter.setObjectName("horizontalfooter")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalfooter.addItem(spacerItem)
        self.themebutton = QtWidgets.QPushButton(self.centralwidget)

        # button for change the theme
        self.themebutton.setMinimumSize(QtCore.QSize(25, 25))
        self.themebutton.setMaximumSize(QtCore.QSize(25, 25))
        self.themebutton.setSizeIncrement(QtCore.QSize(0, 0))
        self.themebutton.setText("")
        self.themebutton.setObjectName("themebutton")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("arrows/sun-shape.svg"), QtGui.QIcon.Normal)
        self.themebutton.setIcon(icon)
        self.themebutton.clicked.connect(self.switchtheme)

        # button for hidden files
        self.hiddenbutton = QtWidgets.QPushButton(self.centralwidget)
        self.hiddenbutton.setMinimumSize(QtCore.QSize(25, 25))
        self.hiddenbutton.setMaximumSize(QtCore.QSize(25, 25))
        self.hiddenbutton.setSizeIncrement(QtCore.QSize(0, 0))
        self.hiddenbutton.setText("")
        self.hiddenbutton.setObjectName("hiddenbutton")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("arrows/hide.svg"), QtGui.QIcon.Normal)
        self.hiddenbutton.setIcon(icon)

        self.hiddenbutton.clicked.connect(self.hiddenitems)

        self.horizontalfooter.addWidget(self.hiddenbutton)
        self.horizontalfooter.addWidget(self.themebutton)
        self.gridLayout.addLayout(self.horizontalfooter, 2, 0, 1, 1)

        path = ""
        self.copyPath = ""
        self.copyList = []
        self.copyListNew = ""

        self.dirModel = QtWidgets.QFileSystemModel()
        self.dirModel.setReadOnly(False)

        self.dirModel.setRootPath(path)

        self.fileModel = QtWidgets.QFileSystemModel()
        self.fileModel.setReadOnly(False)
        # self.fileModel.setResolveSymlinks(True)
        self.fileModel.setRootPath(path)

        self.treeview.setModel(self.dirModel)
        self.treeview.hideColumn(1)
        self.treeview.hideColumn(2)
        self.treeview.hideColumn(3)
        self.treeview.setRootIsDecorated(True)
        # self.treeview.setFocusPolicy(QtCore.Qt.NoFocus)
        # self.listview.setFocusPolicy(QtCore.Qt.NoFocus)

        self.treeview.setExpandsOnDoubleClick(True)
        self.listview.setExpandsOnDoubleClick(True)

        # Ставим параметр табуляции для дерева катологов
        self.treeview.setIndentation(12)
        self.treeview.setTreePosition(0)
        self.treeview.setUniformRowHeights(True)
        self.treeview.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.treeview.setDragEnabled(True)
        self.treeview.setAcceptDrops(True)
        self.treeview.setDropIndicatorShown(True)
        self.treeview.setAnimated(True)

        self.listview.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.treeview.selectionModel().selectionChanged.connect(
            self.on_selectionChanged
        )

        self.listview.setModel(self.fileModel)

        # self.listview.setRootPath(QtCore.QDir.rootPath())

        # self.listview.selectionModel().selectionChanged.connect(self.on_selectionChanged_1)
        # self.listview.setSelectionMode(
        #     QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listview.doubleClicked.connect(self.list_doubleClicked)
        self.treeview.doubleClicked.connect(self.tree_doubleClicked)
        # Устанавливаем свой фокус для проводника
        # self.listview.setFocusPolicy(QtCore.Qt.NoFocus)
        self.listview.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.listview.setAnimated(True)
        self.listview.setDragEnabled(True)
        self.listview.setAcceptDrops(True)
        self.listview.setDropIndicatorShown(True)
        self.listview.sortByColumn(0, QtCore.Qt.AscendingOrder)
        # self.listview.setAllColumnsShowFocus(True)

        self.treeview.sortByColumn(0, QtCore.Qt.AscendingOrder)

        # Переопределение размера для колонок листа #
        self.listview.header().resizeSection(0, 150)
        self.listview.header().resizeSection(1, 80)
        self.listview.header().resizeSection(2, 80)
        self.listview.header().resizeSection(3, 80)
        # self.listview.columnWidth(50)
        ##########################################

        # Включение сортировки для колонок #

        self.listview.setSortingEnabled(True)
        self.treeview.setSortingEnabled(True)

        ##########################################

        self.treeview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listview.setIndentation(10)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.treeview)
        self.splitter.addWidget(self.listview)

        self.verticalalignallprogram.addWidget(self.splitter)

        self.pathbar.setReadOnly(True)

        self._createActions()
        self._createContextMenu()

        self.path_for_backButton = []

        self.check = 0
        self.double_check = 0
        self.theme = 0
        self.cutchecking = False
        self.indexlist = []
        # self.treeview.setFocus()
        self.getRowCount()

    def openDialog(self):
        #       pass
        dialog = ClssDialog(self)
        dialog.exec_()

    def contextMenuEvent(self, event):
        if self.listview.hasFocus():
            self.menu = QtWidgets.QMenu(self.listview)
            if not self.listview.selectionModel().hasSelection():
                self.menu.addAction(self.pasteActionList)
                self.menu.addAction(self.NewFolderAction)
                self.menu.addAction(self.hiddenAction)
            elif self.listview.selectionModel().hasSelection():
                self.menu.addAction(self.copyAction)
                self.menu.addAction(self.delAction)
                self.menu.addAction(self.NewFolderAction)
                self.menu.addAction(self.pasteActionList)
                self.menu.addAction(self.cutAction)
                self.menu.addAction(self.RenameAction)
                self.menu.addAction(self.hiddenAction)
            self.menu.popup(QCursor.pos())
        ######### treeview ############
        elif self.treeview.hasFocus():
            self.menu = QtWidgets.QMenu(self.treeview)
            if not self.treeview.selectionModel().hasSelection():
                self.menu.addAction(self.hiddenAction)
            elif self.treeview.selectionModel().hasSelection():
                self.menu.addAction(self.pasteActionTree)
                self.menu.addAction(self.copyAction)
                self.menu.addAction(self.RenameAction)
                self.menu.addAction(self.cutAction)
                self.menu.addAction(self.delAction)
                self.menu.addAction(self.NewFolderAction)
            self.menu.popup(QCursor.pos())

    def _createContextMenu(self):
        # Setting contextMenuPolicy
        # self.listview.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        # self.treeview.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        # Populating the widget with actions
        self.listview.addAction(self.RenameAction)
        self.listview.addAction(self.NewFolderAction)
        self.listview.addAction(self.delAction)
        self.listview.addAction(self.copyAction)
        self.listview.addAction(self.pasteActionList)
        self.listview.addAction(self.cutAction)
        self.listview.addAction(self.hiddenAction)
        self.treeview.addAction(self.delAction)
        self.treeview.addAction(self.RenameAction)
        self.treeview.addAction(self.NewFolderAction)
        self.treeview.addAction(self.cutAction)
        self.treeview.addAction(self.pasteActionTree)

    def _createActions(self):
        # File actions
        self.RenameAction = QtWidgets.QAction("Rename", triggered=self.renameLIST)
        self.RenameAction.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F2))
        self.RenameAction.setShortcutVisibleInContextMenu(True)
        self.NewFolderAction = QtWidgets.QAction(
            "New Folder", triggered=self.NewFolderLIST
        )
        self.NewFolderAction.setShortcut(QtGui.QKeySequence("Ctrl+n"))
        self.delAction = QtWidgets.QAction("Delete File", triggered=self.deleteFile)
        self.delAction.setShortcut(QtGui.QKeySequence("Del"))
        self.copyAction = QtWidgets.QAction("Copy", triggered=self.copyitems)
        self.pasteActionTree = QtWidgets.QAction("Paste", triggered=self.pasteitemTree)
        self.pasteActionList = QtWidgets.QAction("Paste", triggered=self.pasteitemList)

        self.hiddenAction = QtWidgets.QAction(
            "show hidden Files", triggered=self.hiddenitems
        )
        self.hiddenAction.setCheckable(True)

        self.cutAction = QtWidgets.QAction("Cut file", triggered=self.cutfile)

    def openDialog(self):
        #       pass
        dialog = ClssDialog(self)
        dialog.exec_()

    def hiddenitems(self):
        if self.hiddenEnabled == False:
            self.fileModel.setFilter(
                QtCore.QDir.NoDotAndDotDot
                | QtCore.QDir.Hidden
                | QtCore.QDir.AllDirs
                | QtCore.QDir.Files
            )
            self.dirModel.setFilter(
                QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Hidden | QtCore.QDir.AllDirs
            )
            self.hiddenEnabled = True
            self.hiddenAction.setChecked(True)

            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap("arrows/show.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off
            )

        else:
            self.fileModel.setFilter(
                QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs | QtCore.QDir.Files
            )
            self.dirModel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
            self.hiddenEnabled = False
            self.hiddenAction.setChecked(False)
            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap("arrows/hide.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off
            )
        self.hiddenbutton.setIcon(icon)

    def copyitems(self):
        self.copyList = []
        self.indexlist = []
        if self.listview.hasFocus():
            selected = self.listview.selectionModel().selectedRows()

            for index in selected:
                path = os.path.abspath(
                    self.pathbar.text()
                    + "/"
                    + self.fileModel.data(index, self.fileModel.FileNameRole)
                )
                self.copyList.append(path)
                self.indexlist.append(index)
                # self.clip.setText('\n'.join(self.copyList))

        elif self.treeview.hasFocus():
            selected = self.treeview.selectionModel().selectedRows()

            for index in selected:
                path = os.path.abspath(self.pathbar.text())
                self.copyList.append(path)
                self.indexlist.append(index)

    def pasteitemTree(self):
        msg = QMessageBox.question(
            self,
            "Pasting file",
            "Вы желаете вставить элемент(-ы)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if msg == QMessageBox.Yes:
            if self.treeview.hasFocus:
                for target in self.copyList:
                    destination = os.path.abspath(
                        self.pathbar.text() + "/" + QtCore.QFileInfo(target).fileName()
                    )
                    try:
                        shutil.copytree(target, destination)
                    except OSError as e:
                        if e.errno == errno.ENOTDIR:
                            shutil.copy(target, destination)
            if self.cutchecking:
                for index in self.indexlist:
                    self.fileModel.remove(index)
                self.cutchecking = False
        else:
            pass

    def pasteitemList(self):
        msg = QMessageBox.question(
            self,
            "Pasting file",
            "Вы желаете вставить элемент(-ы)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if msg == QMessageBox.Yes:
            if self.listview.hasFocus:
                for target in self.copyList:
                    destination = os.path.abspath(
                        os.path.abspath(
                            self.fileModel.filePath(
                                self.listview.selectionModel().currentIndex()
                            )
                        )
                        + "/"
                        + QtCore.QFileInfo(target).fileName()
                    )

                    try:
                        shutil.copytree(target, destination)
                    except OSError as e:
                        if e.errno == errno.ENOTDIR:
                            shutil.copy(target, destination)

            if self.cutchecking:
                for index in self.indexlist:
                    self.fileModel.remove(index)
                self.cutchecking = False
        else:
            pass

    def switchtheme(self):
        if self.theme == 0:
            self.setStyleSheet(mystylesheetlight(self))
            self.theme += 1

            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap("arrows/moon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off
            )

        elif self.theme == 1:
            self.setStyleSheet(mystylesheetdark(self))
            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap("arrows/sun-shape.svg"),
                QtGui.QIcon.Normal,
                QtGui.QIcon.Off,
            )
            self.theme = 0
        self.themebutton.setIcon(icon)

    def renameLIST(self):
        if self.listview.hasFocus():
            self.fileModel.setReadOnly(False)
            d = os.path.abspath(
                self.fileModel.filePath(self.listview.selectionModel().currentIndex())
            )
            ix = self.fileModel.index(d)
            QtCore.QTimer.singleShot(0, lambda ix=ix: self.listview.setCurrentIndex(ix))
            QtCore.QTimer.singleShot(0, lambda ix=ix: self.listview.edit(ix))
        elif self.treeview.hasFocus():
            self.renameTREE()

    def renameTREE(self):
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()

        ix = self.dirModel.index(path)
        QtCore.QTimer.singleShot(0, lambda ix=ix: self.treeview.setCurrentIndex(ix))
        QtCore.QTimer.singleShot(0, lambda ix=ix: self.treeview.edit(ix))

    def NewFolderLIST(self):
        try:
            if self.listview.hasFocus():
                self.fileModel.setReadOnly(False)
                dest = os.path.abspath(self.pathbar.text() + "/New folder")
                if not os.path.exists(dest):
                    os.mkdir(dest)
                ix = self.fileModel.index(dest)
                QtCore.QTimer.singleShot(
                    0, lambda ix=ix: self.listview.setCurrentIndex(ix)
                )
                QtCore.QTimer.singleShot(0, lambda ix=ix: self.listview.edit(ix))
                ix = self.fileModel.index(os.path.abspath(self.pathbar.text()))
                self.listview.setCurrentIndex(ix)
            elif self.treeview.hasFocus():
                self.NewFolderTREE()
        except:
            pass

    def NewFolderTREE(self):
        try:
            self.dirModel.setReadOnly(False)
            dest = os.path.abspath(self.pathbar.text() + "/New folder")
            if not os.path.exists(dest):
                os.mkdir(dest)
            ix = self.dirModel.index(dest)
            # QtCore.QTimer.singleShot(
            #     0, lambda ix=ix: self.treeview.setCurrentIndex(ix))
            QtCore.QTimer.singleShot(0, lambda ix=ix: self.treeview.edit(ix))
            ix = self.dirModel.index(os.path.abspath(self.pathbar.text()))
            self.treeview.setCurrentIndex(ix)
        except:
            pass

    def cutfile(self):
        msg = QMessageBox.question(
            self,
            "Deleting file",
            "Вы желаете вырезать элемент(-ы)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if msg == QMessageBox.Yes:
            self.copyitems()
            self.cutchecking = True
        else:
            pass

    def deletetree(self):
        # pass

        index = self.treeview.selectionModel().currentIndex()
        delFolder = self.dirModel.fileInfo(index).absoluteFilePath()

        msg = QMessageBox.question(
            self,
            "Deleting file",
            f"""Вы желаете удалить элемент(-ы) {self.dirModel.fileName(index)}?""",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if msg == QMessageBox.Yes:
            self.fileModel.remove(index)
        else:
            pass

    def deleteFile(self):
        if self.listview.hasFocus():
            index = self.listview.selectionModel().selectedIndexes()

            msg = QMessageBox.question(
                self,
                "Deleting file",
                f"Вы желаете удалить элемент(-ы)?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            # self.copyPath = self.fileModel.fileInfo(
            #     index).absoluteFilePath()
            if msg == QMessageBox.Yes:
                for delFile in self.listview.selectionModel().selectedIndexes():
                    self.fileModel.remove(delFile)
            else:
                pass
        elif self.treeview.hasFocus():
            self.deletetree()

    def goUp_click(self):
        self.listview.selectionModel().clearSelection()
        newpath = (
            os.path.dirname(self.pathbar.text()) if len(self.pathbar.text()) > 3 else ""
        )

        # self.treeview.setCurrentIndex(self.dirModel.setRootPath(path))
        self.listview.setRootIndex(self.fileModel.setRootPath(newpath))

        self.path_for_backButton.append(
            "" if self.pathbar.text() == "Drives" else self.pathbar.text()
        )
        self.row_for_back(newpath)

    def back_click(self):
        self.list_clear()
        try:
            backup = self.path_for_backButton.pop()
            self.listview.setRootIndex(self.fileModel.index(backup))
            self.row_for_back(backup + "/" if len(backup) == 2 else backup)

        except:
            self.listview.setRootIndex(self.fileModel.index(""))
            self.row_for_back("")
        self.listview.clearSelection()

    def pathbar_dest(self, path):
        self.pathbar.setText(path if path != "" else "Drives")

    def getRowCount(self):
        index = self.listview.selectionModel().currentIndex()
        path = QtCore.QDir(self.fileModel.fileInfo(index).absoluteFilePath())
        count = len(path.entryList(QtCore.QDir.Files))

        index_for_checker = self.listview.selectionModel().currentIndex()
        check = self.fileModel.fileInfo(index_for_checker).absoluteFilePath()

        if check == "":
            count = 0

        self.statusbar.showMessage(f"{count} files", 0)

        self.pathbar_dest(check)

        return count

    def getRowCount_tree(self):
        index = self.treeview.selectionModel().currentIndex()
        path1 = QtCore.QDir(self.dirModel.fileInfo(index).absoluteFilePath())
        count = len(path1.entryList(QtCore.QDir.Files))

        index_for_checker = self.treeview.selectionModel().currentIndex()
        check = self.dirModel.fileInfo(index_for_checker).absoluteFilePath()

        self.statusbar.showMessage(f"{count} files", 0)

        self.pathbar_dest(check)

        return count

    def row_for_back(self, path):
        path_checker = QtCore.QDir(path)
        count = len(path_checker.entryList(QtCore.QDir.Files))

        if path == "":
            count = 0

        self.statusbar.showMessage(f"{count} files", 0)

        self.pathbar_dest(path)

        return count

    def on_selectionChanged(self):
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        self.listview.setRootIndex(self.fileModel.setRootPath(path))
        if not self.dirModel.fileInfo(index).isDir():
            pass
        self.listview.clearFocus()
        self.path_for_backButton.append(
            "" if self.pathbar.text() == "Drives" else self.pathbar.text()
        )
        self.getRowCount_tree()

    def tree_doubleClicked(self):
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()

        if not self.dirModel.fileInfo(index).isDir():
            os.startfile(str(path))
        else:
            self.listview.setRootIndex(self.fileModel.setRootPath(path))

    def list_doubleClicked(self):
        self.fileModel.setReadOnly(True)

        index = self.listview.selectionModel().currentIndex()
        path = self.fileModel.fileInfo(index).absoluteFilePath()

        if not self.fileModel.fileInfo(index).isDir():
            os.startfile(os.path.abspath(path))
        else:
            self.path_for_backButton.append(
                "" if self.pathbar.text() == "Drives" else self.pathbar.text()
            )
            self.treeview.setCurrentIndex(self.dirModel.index(path[:3]))
            self.listview.setRootIndex(self.fileModel.setRootPath(path))
            self.getRowCount()

    def list_clear(self):
        for i in range(len(self.path_for_backButton)):
            try:
                if self.path_for_backButton[i] == self.path_for_backButton[i + 1]:
                    self.path_for_backButton.remove(self.path_for_backButton[i])

            except:
                pass
        print(self.path_for_backButton)

    def count_path(self, p):
        k = ""
        for i in range(len(p) - 1, -1, -1):
            if p[i] == "/":
                k += p[i]
                break
            k += p[i]
        return len(k)


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

QLineEdit#pathbar{
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
    background-color: transparent;
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

    QLineEdit#pathbar{
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

    MainWindow.listview.setRootIndex(MainWindow.fileModel.index(""))
    MainWindow.treeview.setRootIndex(MainWindow.dirModel.index(""))

    MainWindow.setWindowTitle("FileManager")
    sys.exit(app.exec_())
