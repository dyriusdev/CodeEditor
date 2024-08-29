from PyQt5.QtWidgets import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pathlib import Path
from editor import Editor

import sys
import os
import resources

class MainWindow(QMainWindow):
    
    def __init__(self) -> None:
        super(QMainWindow, self).__init__()
        self.sideBarClr : str = "#282c34"
        self.currentFile : Path = None
        
        self.InitUI()
        pass
    
    def InitUI(self) -> None:
        self.setWindowTitle("PyQt Editor")
        self.resize(1280, 720)
        
        self.window_font : QFont = QFont("FireCode")
        self.window_font.setPointSize(12)
        self.setFont(self.window_font)
        self.setStyleSheet(open("./src/css/style.qss", "r").read())
        
        self.SetupMenu()
        self.SetupBody()
        self.show()
        pass
    
    def SetupMenu(self) -> None:
        menuBar = self.menuBar()
        
        fileMenu : QMenu = menuBar.addMenu("File")
        
        newFile : QAction = fileMenu.addAction("New File")
        newFile.setShortcut("Ctrl+N")
        newFile.triggered.connect(self.NewFile)
        
        openFile : QAction = fileMenu.addAction("Open File")
        openFile.setShortcut("Ctrl+O")
        openFile.triggered.connect(self.OpenFile)
        
        openFolder : QAction = fileMenu.addAction("Open Folder")
        openFolder.setShortcut("Ctrl+Shift+O")
        openFolder.triggered.connect(self.OpenFolder)
        
        fileMenu.addSeparator()
        
        saveFile : QAction = fileMenu.addAction("Save")
        saveFile.setShortcut("Ctrl+S")
        saveFile.triggered.connect(self.SaveFile)
        
        saveFileAs : QAction = fileMenu.addAction("Save As")
        saveFileAs.setShortcut("Ctrl+Shift+S")
        saveFileAs.triggered.connect(self.SaveAs)
        
        editMenu : QMenu = menuBar.addMenu("Edit")
        
        copyAction : QAction = editMenu.addAction("Copy")
        copyAction.setShortcut("Ctrl+C")
        copyAction.triggered.connect(self.CopyAction)
        
        pass
    
    def NewFile(self) -> None:
        self.SetNewTab(None, True)
        pass
    
    def SaveFile(self) -> None:
        if self.currentFile is None and self.tabView.count() > 0:
            self.SaveAs()
        
        editor : QWidget = self.tabView.currentWidget()
        self.currentFile.write_text(editor.text())
        self.statusBar().showMessage(f"Saved {self.currentFile.name}", 2000)
        pass
    
    def SaveAs(self) -> None:
        editor : QWidget = self.tabView.currentWidget()
        if editor is None:
            return

        filePath : str = QFileDialog.getSaveFileName(self, "Save As", os.getcwd())[0]
        if filePath == "":
            self.statusBar().showMessage("Cancelled", 2000)
            return

        path : Path = Path(filePath)
        path.write_text(editor.text())
        self.tabView.setTabText(self.tabView.currentIndex(), path.name)
        self.statusBar().showMessage(f"Saved {path.name}", 2000)
        self.currentFile = path
        pass
    
    def OpenFile(self) -> None:
        ops : QFileDialog.Options = QFileDialog.Options()
        newFile, _ = QFileDialog.getOpenFileName(self, "Pick a file", "", "All files (*);;Python Files (*.py)", options=ops)
        if newFile == "":
            self.statusBar().showMessage("Cancelled", 2000)
            return
        
        f : Path = Path(newFile)
        self.SetNewTab(f)
        pass
    
    def OpenFolder(self) -> None:
        ops : QFileDialog.Options = QFileDialog.Options()
        newFolder = QFileDialog.getExistingDirectory(self, "Pick a folder", "", options=ops)
        if newFolder:
            self.model.setRootPath(newFolder)
            self.treeView.setRootIndex(self.model.index(newFolder))
            self.statusBar().showMessage(f"Opened {newFolder}", 2000)
        pass
    
    def CopyAction(self) -> None:
        editor : QWidget = self.tabView.currentWidget()
        if editor is not None:
            editor.copy()
        pass
    
    def SetupBody(self) -> None:
        bodyFrame : QFrame = QFrame()
        bodyFrame.setFrameShape(QFrame.NoFrame)
        bodyFrame.setFrameShadow(QFrame.Plain)
        bodyFrame.setLineWidth(0)
        bodyFrame.setMidLineWidth(0)
        bodyFrame.setContentsMargins(0, 0, 0, 0)
        bodyFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body : QHBoxLayout = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        bodyFrame.setLayout(body)
        
        self.sideBar : QFrame = QFrame()
        self.sideBar.setFrameShape(QFrame.StyledPanel)
        self.sideBar.setFrameShadow(QFrame.Plain)
        self.sideBar.setStyleSheet(f'''
            background-color: {self.sideBarClr};
        ''')
        sideBarLayout : QHBoxLayout = QHBoxLayout()
        sideBarLayout.setContentsMargins(5, 10, 5, 0)
        sideBarLayout.setSpacing(0)
        sideBarLayout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        
        folderLabel : QLabel = self.GetSideBarLabel("./src/icons/folder.svg", "folder.svg")
        sideBarLayout.addWidget(folderLabel)
        self.sideBar.setLayout(sideBarLayout)
        
        body.addWidget(self.sideBar)
        self.hSplit : QSplitter = QSplitter(Qt.Horizontal)
        self.treeFrame : QFrame = QFrame()
        self.treeFrame.setContentsMargins(0, 0, 0, 0)
        self.treeFrame.setLineWidth(1)
        self.treeFrame.setMaximumWidth(400)
        self.treeFrame.setMinimumWidth(200)
        self.treeFrame.setBaseSize(100, 0)
        treeLayout : QVBoxLayout = QVBoxLayout()
        treeLayout.setContentsMargins(0, 0, 0, 0)
        treeLayout.setSpacing(0)
        self.treeFrame.setStyleSheet('''
            QFrame {
                background-color: #21252b;
                border-radius: 5px;
                border: none;
                padding: 5px;
                color: #D3D3D3;    
            }
            QFrame:hover {
                color: white;
            }
        ''')
        
        self.model : QFileSystemModel = QFileSystemModel()
        self.model.setRootPath(os.getcwd())
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
        
        self.treeView : QTreeView = QTreeView()
        self.treeView.setFont(QFont("FireCode", 13))
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index(os.getcwd()))
        self.treeView.setSelectionMode(QTreeView.SingleSelection)
        self.treeView.setSelectionBehavior(QTreeView.SelectRows)
        self.treeView.setEditTriggers(QTreeView.NoEditTriggers)

        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.TreeViewContextMenu)
        
        self.treeView.clicked.connect(self.TreeViewClicked)
        self.treeView.setIndentation(10)
        self.treeView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.treeView.setHeaderHidden(True)
        self.treeView.setColumnHidden(1, True)
        self.treeView.setColumnHidden(2, True)
        self.treeView.setColumnHidden(3, True)
        
        treeLayout.addWidget(self.treeView)
        self.treeFrame.setLayout(treeLayout)
        
        self.tabView : QTabWidget = QTabWidget()
        self.tabView.setContentsMargins(0, 0, 0, 0)
        self.tabView.setTabsClosable(True)
        self.tabView.setMovable(True)
        self.tabView.setDocumentMode(True)
        self.tabView.tabCloseRequested.connect(self.CloseTab)
        
        self.hSplit.addWidget(self.treeFrame)
        self.hSplit.addWidget(self.tabView)
        
        body.addWidget(self.hSplit)
        bodyFrame.setLayout(body)
        self.setCentralWidget(bodyFrame)
        pass
    
    def ShowHideTab(self, e, type) -> None:
        if self.treeFrame.isHidden():
            self.treeFrame.show()
        else:
            self.treeFrame.hide()
        pass
    
    def CloseTab(self, index : int) -> None:
        self.tabView.removeTab(index)
        pass
    
    def TreeViewContextMenu(self, pos : int) -> None:
        pass
    
    def TreeViewClicked(self, index : QModelIndex) -> None:
        path = self.model.filePath(index)
        p = Path(path)
        self.SetNewTab(p)
        pass
    
    def GetEditor(self) -> Editor:
        return Editor()
    
    def IsBinary(self, path : Path) -> bool:
        with open(path, "rb") as f:
            return b"\0" in f.read(1024)
    
    def SetNewTab(self, path : Path, isNewFile : bool = False) -> None:
        editor : Editor = self.GetEditor()
        if isNewFile:
            self.tabView.addTab(editor, "untitled")
            self.setWindowTitle("untitled")
            self.statusBar().showMessage("Opened untitled")
            self.tabView.setCurrentIndex(self.tabView.count() - 1)
            self.currentFile = None
            return
        
        if not path.is_file():
            return
        if self.IsBinary(path):
            self.statusBar().showMessage("Cannot open binary file", 2000)
            return
        
        for i in range(self.tabView.count()):
            if self.tabView.tabText(i) == path.name:
                self.tabView.setCurrentIndex(i)
                self.currentFile = path
                return

        self.tabView.addTab(editor, path.name)
        editor.setText(path.read_text())
        self.setWindowTitle(path.name)
        self.currentFile = path
        self.tabView.setCurrentIndex(self.tabView.count() - 1)
        self.statusBar().showMessage(f"Opened {path.name}", 2000)
        pass
    
    def GetSideBarLabel(self, path, name) -> QLabel:
        label : QLabel = QLabel()
        label.setPixmap(QPixmap(path).scaled(QSize(25, 25)))
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        label.setFont(self.window_font)
        label.mousePressEvent = lambda e: self.ShowHideTab(e, name)
        return label


if __name__ == "__main__":
    app : QApplication = QApplication([])
    window : MainWindow = MainWindow()
    sys.exit(app.exec())