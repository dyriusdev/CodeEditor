from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QListWidgetItem
from pathlib import Path

import os
import re

class SearchItem(QListWidgetItem):
    
    def __init__(self, name, fullPath, lineOn, end, line) -> None:
        self.name = name
        self.fullPath = fullPath
        self.lineOn = lineOn
        self.end = end
        self.line = line
        self.formatted = f"{self.name}:{self.lineOn}:{self.end} - {self.line} ..."
        super().__init__(self.formatted)
        pass
    
    def __str__(self) -> str:
        return self.formatted
    
    def __repr__(self) -> str:
        return self.formatted

class SearchWorker(QThread):
    finished = pyqtSignal(list)
    
    def __init__(self) -> None:
        super(SearchWorker, self).__init__(None)
        self.items = []
        self.searchPath : str = None
        self.searchText : str = None
        self.searchProject : bool = None
        pass
    
    def run(self) -> None:
        self.Search()
        pass
    
    def Update(self, pattern, path, searchProject) -> None:
        self.searchText = pattern
        self.searchPath = path
        self.searchProject = searchProject
        self.start()
        pass
    
    def Search(self):
        debug = False
        self.items = []
        excludeDirs = set([".git", ".svn", ".hg", ".bzr", ".idea", "__pycache", "venv"])
        if self.searchProject:
            excludeDirs.remove("venv")
        excludeFiles = set([".svg", ".png", ".exe", ".pyc", ".qm"])
        
        for root, _, files in self.WalkDir(self.searchPath, excludeDirs, excludeFiles):
            if len(self.items) > 5_000:
                break
            for file in files:
                fullPath = os.path.join(root, file)
                if self.IsBinary(fullPath):
                    break
                try:
                    with open(fullPath, "r", encoding="utf8") as f:
                        try:
                            reg = re.compile(self.searchText, re.IGNORECASE)
                            for i, line in enumerate(f):
                                if m := reg.search(line):
                                    fd = SearchItem(
                                        file,
                                        fullPath,
                                        i,
                                        m.end(),
                                        line[m.start():].strip()[:50]
                                    )
                                    self.items.append(fd)
                        except re.error as e:
                            if debug: print(e)
                except UnicodeDecodeError as e:
                    if debug: print(e)
                    continue
        self.finished.emit(self.items)
        pass
    
    def IsBinary(self, path : Path) -> bool:
        with open(path, "rb") as f:
            return b"\0" in f.read(1024)
    
    def WalkDir(self, path, excludeDirs : list[str], excludeFiles : list[str]):
        for root, dirs, files in os.walk(path, topdown=True):
            dirs[:] = [d for d in dirs if d not in excludeDirs]
            files[:] = [f for f in files if Path(f).suffix not in excludeFiles]
            yield root, dirs, files
            
        pass