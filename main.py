from PyQt5 import QtCore, QtGui, QtWidgets
import os
import sys
import subprocess
import shutil
import errno


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        MainWindow.setStyleSheet(mystylesheetdark(self))

        self.hiddenEnabled = False
        self.clip = QtWidgets.QApplication.clipboard()
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setMaximumSize(QtCore.QSize(100, 100))
        self.pushButton.setMinimumSize(QtCore.QSize(25, 25))
        self.pushButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("arrows/left-arrow.svg"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.back_click)

        self.horizontalLayout_2.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setMaximumSize(QtCore.QSize(100, 100))
        self.pushButton_2.setMinimumSize(QtCore.QSize(25, 25))
        self.pushButton_2.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("arrows/up-arrow.svg"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon1)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_2.addWidget(self.pushButton_2)

        self.pushButton_2.clicked.connect(self.goUp_click)

        self.pathbar = QtWidgets.QLineEdit(self.centralwidget)
        self.pathbar.setMinimumSize(QtCore.QSize(20, 20))
        self.pathbar.setObjectName("pathbar")
        self.horizontalLayout_2.addWidget(self.pathbar)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.treeview = QtWidgets.QTreeView(self.centralwidget)
        self.treeview.setMaximumSize(QtCore.QSize(250, 16777215))
        self.treeview.setObjectName("treeview")

        self.listview = QtWidgets.QTreeView(self.centralwidget)
        self.listview.setObjectName("listview")

        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)

        self.pushButton_4.setMinimumSize(QtCore.QSize(25, 25))
        self.pushButton_4.setMaximumSize(QtCore.QSize(25, 25))
        self.pushButton_4.setSizeIncrement(QtCore.QSize(0, 0))
        self.pushButton_4.setText("")
        self.pushButton_4.setObjectName("pushButton_4")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("arrows/sun-shape.svg"),
                       QtGui.QIcon.Normal)

        self.pushButton_4.setIcon(icon)

        self.pushButton_4.clicked.connect(self.switchtheme)

        self.horizontalLayout_3.addWidget(self.pushButton_4)
        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)

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

        self.listview.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.treeview.selectionModel().selectionChanged.connect(self.on_selectionChanged)

        self.listview.setModel(self.fileModel)

        # self.listview.setRootPath(QtCore.QDir.rootPath())

        # self.listview.selectionModel().selectionChanged.connect(self.on_selectionChanged_1)
        # self.listview.setSelectionMode(
        #     QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listview.doubleClicked.connect(self.list_doubleClicked)
        # Устанавливаем свой фокус для проводника
        # self.listview.setFocusPolicy(QtCore.Qt.NoFocus)
        self.listview.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.listview.setDragEnabled(True)
        self.listview.setAcceptDrops(True)
        self.listview.setDropIndicatorShown(True)
        self.listview.sortByColumn(0, QtCore.Qt.AscendingOrder)

        self.treeview.sortByColumn(0, QtCore.Qt.AscendingOrder)

        # Переопределение размера для колонок листа #

        self.listview.header().resizeSection(0, 250)
        self.listview.header().resizeSection(1, 80)
        self.listview.header().resizeSection(2, 80)

        ##########################################

        # Включение сортировки для колонок #

        self.listview.setSortingEnabled(True)
        self.treeview.setSortingEnabled(True)

        ##########################################

        self.treeview.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listview.setIndentation(10)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.treeview)
        self.splitter.addWidget(self.listview)

        self.verticalLayout.addWidget(self.splitter)

        self.pathbar.setReadOnly(True)

        self._createActions()
        self._createContextMenu()

        self.path_for_backButton = []

        self.check = 0
        self.double_check = 0
        self.theme = 0
        self.getRowCount()

    def _createContextMenu(self):
        # Setting contextMenuPolicy
        self.listview.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.treeview.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        # Populating the widget with actions
        self.listview.addAction(self.RenameAction)
        self.listview.addAction(self.NewFolderAction)
        self.listview.addAction(self.delAction)
        self.listview.addAction(self.copyAction)
        self.listview.addAction(self.pasteAction)
        self.treeview.addAction(self.delAction)
        self.treeview.addAction(self.RenameAction)
        self.treeview.addAction(self.NewFolderAction)

    def _createActions(self):
        # File actions
        self.RenameAction = QtWidgets.QAction(
            "Rename", triggered=self.renameLIST)
        self.RenameAction.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F2))
        self.NewFolderAction = QtWidgets.QAction(
            "New Folder", triggered=self.NewFolderLIST)
        self.NewFolderAction.setShortcut(QtGui.QKeySequence("Ctrl+N"))
        self.delAction = QtWidgets.QAction(
            "Delete File",  triggered=self.deleteFile)
        self.delAction.setShortcut(QtGui.QKeySequence("Del"))
        self.copyAction = QtWidgets.QAction(
            "Copy",  triggered=self.copyitem)
        self.pasteAction = QtWidgets.QAction(
            "Paste",  triggered=self.pasteitem)

    def copyitem(self):
        self.copyList = []
        # index = self.listview.selectionModel().currentIndex()
        # folderpath = self.fileModel.fileInfo(index).absoluteFilePath()
        selected = self.listview.selectionModel().selectedRows()

        for index in selected:
            path = self.pathbar.text() + "/" + \
                self.fileModel.data(index, self.fileModel.FileNameRole)
            # print(path, "copied to clipboard")
            self.copyList.append(path)
            self.clip.setText('\n'.join(self.copyList))

        # print("%s\n%s" % ("folderpath copied:", folderpath))
        # self.folder_copied = folderpath
        # self.copyList.append(self.folder_copied)

    def pasteitem(self):
        for i in self.copyList:
            target = i
            destination = self.pathbar.text() + "/" + \
                QtCore.QFileInfo(target).fileName()
            # print("%s %s %s" % (target, "will be pasted to", destination))
            try:
                shutil.copytree(target, destination)
            except OSError as e:
                # If the error was caused because the source wasn't a directory
                if e.errno == errno.ENOTDIR:
                    shutil.copy(target, destination)

    # def copyFolder(self):
    #     index = self.treeview.selectionModel().currentIndex()
    #     folderpath = self.dirModel.fileInfo(index).absoluteFilePath()
    #     print("%s\n%s" % ("folderpath copied:", folderpath))
    #     self.folder_copied = folderpath
    #     self.copyList = []

    def switchtheme(self):
        if self.theme == 0:

            MainWindow.setStyleSheet(mystylesheetlight(self))
            self.theme += 1

            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("arrows/moon.svg"),
                           QtGui.QIcon.Normal, QtGui.QIcon.Off)

        elif self.theme == 1:
            MainWindow.setStyleSheet(mystylesheetdark(self))
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("arrows/sun-shape.svg"),
                           QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.theme = 0
        self.pushButton_4.setIcon(icon)

    def renameLIST(self):
        if self.listview.hasFocus():
            self.fileModel.setReadOnly(False)
            d = str(self.fileModel.filePath(
                self.listview.selectionModel().currentIndex()))
            ix = self.fileModel.index(d)
            QtCore.QTimer.singleShot(
                0, lambda ix=ix: self.listview.setCurrentIndex(ix))
            QtCore.QTimer.singleShot(0, lambda ix=ix: self.listview.edit(ix))
        elif self.treeview.hasFocus():
            self.renameTREE()

    def renameTREE(self):
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        d = str(path)

        ix = self.dirModel.index(d)
        QtCore.QTimer.singleShot(
            0, lambda ix=ix: self.treeview.setCurrentIndex(ix))
        QtCore.QTimer.singleShot(0, lambda ix=ix: self.treeview.edit(ix))

    def NewFolderLIST(self):
        try:
            if self.listview.hasFocus():
                self.fileModel.setReadOnly(False)
                if not os.path.exists(self.pathbar.text() + '/New folder'):
                    os.mkdir(self.pathbar.text() + '/New folder')
                ix = self.fileModel.index(self.pathbar.text() + '/New folder')
                QtCore.QTimer.singleShot(
                    0, lambda ix=ix: self.listview.setCurrentIndex(ix))
                QtCore.QTimer.singleShot(
                    0, lambda ix=ix: self.listview.edit(ix))
                ix = self.fileModel.index(self.pathbar.text())
                self.listview.setCurrentIndex(ix)
            elif self.treeview.hasFocus():
                self.NewFolderTREE()
            self.listview.selectionModel.clear()
        except:
            pass

    def NewFolderTREE(self):
        try:
            self.dirModel.setReadOnly(False)
            if not os.path.exists(self.pathbar.text() + '/New folder'):
                os.mkdir(self.pathbar.text() + '/New folder')
            ix = self.dirModel.index(self.pathbar.text() + '/New folder')
            QtCore.QTimer.singleShot(
                0, lambda ix=ix: self.treeview.setCurrentIndex(ix))
            QtCore.QTimer.singleShot(
                0, lambda ix=ix: self.treeview.edit(ix))
            ix = self.dirModel.index(self.pathbar.text())
            self.treeview.setCurrentIndex(ix)
        except:
            pass

    def deleteFolder(self):
        pass
        # index = self.treeview.selectionModel().currentIndex()
        # delFolder = self.dirModel.fileInfo(index).absoluteFilePath()

        # print('Deletion confirmed.')
        # self.statusbar.showMessage("%s %s" % ("folder deleted", delFolder), 0)
        # self.fileModel.remove(index)
        # print("%s %s" % ("folder deleted", delFolder))

    def deleteFile(self):
        pass
        # if self.listview.hasFocus():
        #     print('Deletion confirmed.')
        #     index = self.listview.selectionModel().currentIndex()
        #     self.copyPath = self.fileModel.fileInfo(index).absoluteFilePath()
        #     print("%s %s" % ("file deleted", self.copyPath))
        #     self.statusbar.showMessage("%s %s" % (
        #         "file deleted", self.copyPath), 0)
        #     for delFile in self.listview.selectionModel().selectedIndexes():
        #         self.fileModel.remove(delFile)
        # elif self.treeview.hasFocus():
        #     self.deleteFolder()

    def goUp_click(self):
        try:
            self.listview.selectionModel().clearSelection()
            self.treeview.selectionModel().clearSelection()
            newpath = self.path_go_up(self.pathbar.text())
            # self.treeview.setCurrentIndex(self.dirModel.setRootPath(path))
            self.listview.setRootIndex(
                self.fileModel.setRootPath(newpath))

            self.row_for_back(newpath)
            self.listview.selectionModel().clearSelection()
            self.treeview.selectionModel().clearSelection()
        except:
            pass

        # if self.check == 0:
        #     if self.double_check == 1:
        #         self.listview.setRootIndex(
        #             self.fileModel.index(""))

        #     else:
        #         index = self.listview.selectionModel().currentIndex()
        #         self.back_path = self.fileModel.fileInfo(index).path()
        #         self.listview.setRootIndex(
        #             self.fileModel.index(self.back_path))
        #         self.listview.selectionModel().clearSelection()
        #         self.check += 1
        #         self.double_check = 0
        #     self.row_for_back(self.back_path)

        # else:
        #     if len(self.back_path) == 3:
        #         self.listview.setRootIndex(
        #             self.fileModel.index(""))
        #         self.back_path = ""
        #     else:
        #         self.back_path = self.back_path[:len(
        #             self.back_path)-self.count_path(self.back_path)]
        #         self.listview.setRootIndex(
        #             self.fileModel.index(self.back_path))
        #     if self.back_path == "":
        #         self.check = 0
        #         self.double_check = 1
        #     self.listview.selectionModel().clearSelection()
        #     self.row_for_back(self.back_path + "/" if len(
        #         self.back_path) == 2 else self.back_path)

    def back_click(self):
        self.spisik_path()
        try:
            backup = self.path_for_backButton.pop()
            self.listview.setRootIndex(
                self.fileModel.index(backup))
            self.row_for_back(backup + "/" if len(
                backup) == 2 else backup)
        except:
            self.listview.setRootIndex(
                self.fileModel.index(""))
            self.row_for_back("")

    def pathbar_dest(self, check):
        self.pathbar.setText(
            check) if check != "" else self.pathbar.setText("Drives")

    def getRowCount(self):
        index = self.listview.selectionModel().currentIndex()
        path1 = QtCore.QDir(self.fileModel.fileInfo(index).absoluteFilePath())
        count = len(path1.entryList(QtCore.QDir.Files))

        index_for_checker = self.listview.selectionModel().currentIndex()
        check = self.fileModel.fileInfo(index_for_checker).absoluteFilePath()

        if check == "":
            count = 0

        self.statusbar.showMessage("%s %s" %
                                   (count, "Files"), 0)

        self.pathbar_dest(check)

        return count

    def getRowCount_tree(self):
        index = self.treeview.selectionModel().currentIndex()
        path1 = QtCore.QDir(self.dirModel.fileInfo(index).absoluteFilePath())
        count = len(path1.entryList(QtCore.QDir.Files))

        index_for_checker = self.treeview.selectionModel().currentIndex()
        check = self.dirModel.fileInfo(index_for_checker).absoluteFilePath()

        self.statusbar.showMessage("%s %s" %
                                   (count, "Files"), 0)

        self.pathbar_dest(check)

        return count

    def row_for_back(self, path):
        path1 = QtCore.QDir(path)
        count = len(path1.entryList(QtCore.QDir.Files))

        if path == "":
            count = 0

        self.statusbar.showMessage("%s %s" %
                                   (count, "Files"), 0)

        self.pathbar_dest(path)

        return count

    def on_selectionChanged(self):

        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        self.listview.setRootIndex(self.fileModel.setRootPath(path))
        self.currentPath = path
        if not self.dirModel.fileInfo(index).isDir():
            os.startfile(str(path))
        self.treeview.setFocus()
        self.listview.clearFocus()

        self.getRowCount_tree()

    def count_path(self, p):
        k = ""
        for i in range(len(p)-1, -1, -1):
            if p[i] == "/":
                k += p[i]
                break
            k += p[i]
        return (len(k))

    def list_doubleClicked(self):
        self.fileModel.setReadOnly(True)
        index = self.listview.selectionModel().currentIndex()
        path = self.fileModel.fileInfo(index).absoluteFilePath()
        # self.check = 0
        # self.double_check = 0
        self.path_for_backButton.append(path[:len(
            path)-self.count_path(path)])

        if not self.fileModel.fileInfo(index).isDir():
            os.startfile(str(path))
            self.listview.setCurrentIndex(self.fileModel.setRootPath(path))
        else:
            self.listview.setRootIndex(self.fileModel.setRootPath(path))
            # self.treeview.setCurrentIndex(self.dirModel.setRootPath(path))
            # self.treeview.setFocusPolicy(QtCore.Qt.NoFocus)
            self.listview.setFocus()
            self.getRowCount()
        # self.fileModel.setReadOnly(False)

    def path_go_up(self, p):
        k = ""
        for i in range(len(p)-1, -1, -1):
            if p[i] == "/":
                k += p[i]
                break
            k += p[i]

        if len(k) == len(p):
            res = ""
        else:
            res = p[:-(len(k))]
        if len(p) == 3:
            res = ""
        if len(res) == 2:
            res += "/"
        return (res)

    def spisik_path(self):
        for i in range(len(self.path_for_backButton)):
            try:
                if self.path_for_backButton[i] == self.path_for_backButton[i+1]:
                    self.path_for_backButton.remove(
                        self.path_for_backButton[i])
            except:
                pass


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
    selection-background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #729fcf, stop: 1  #204a87);
}
QTreeView::item{
height: 22px;
color: black;
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
height: 22px;
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
    """


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    ui.listview.setRootIndex(
        ui.fileModel.index(""))
    ui.treeview.setRootIndex(
        ui.dirModel.index(""))

    MainWindow.setWindowTitle("FileManager")
    sys.exit(app.exec_())
