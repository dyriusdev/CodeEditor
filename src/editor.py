from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget
from pathlib import Path

from lexer import PyCustomLexer
from autocomplete import AutoComplete

import keyword
import pkgutil

class Editor(QsciScintilla):
    
    def __init__(self, parent: QWidget = None, path : Path = None, isPythonFile : bool = True) -> None:
        super(Editor, self).__init__(parent)
        self.path : Path = path
        self.fullPath : Path = self.path.absolute()
        self.isPythonFile : bool = isPythonFile
        
        self.cursorPositionChanged.connect(self.CursorPositionChanged)
        
        self.window_font : QFont = QFont("FireCode")
        self.window_font.setPointSize(12)
        self.setFont(self.window_font)
        self.setUtf8(True)
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        
        self.setIndentationGuides(True)
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)
        
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)
        
        self.setCaretForegroundColor(QColor("#dedcdc"))
        self.setCaretLineVisible(True)
        self.setCaretWidth(2)
        self.setCaretLineBackgroundColor(QColor("#2c313c"))
        
        self.setEolMode(QsciScintilla.EolUnix)
        self.setEolVisibility(False)
        
        if self.isPythonFile:
            self.pyLexer : PyCustomLexer = PyCustomLexer(self)
            self.pyLexer.setDefaultFont(self.window_font)
            
            self.api : QsciAPIs = QsciAPIs(self.pyLexer)
            
            self.autoCompleter : AutoComplete = AutoComplete(self.fullPath, self.api)
            self.autoCompleter.finished.connect(self.LoadedAutoCompleter)
            self.setLexer(self.pyLexer)
        else:
            self.setPaper(QColor("#282c34"))
            self.setColor("#abb2bf")
        
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setMarginsForegroundColor(QColor("#ff888888"))
        self.setMarginsBackgroundColor(QColor("#282c34"))
        self.setMarginsFont(self.window_font)
        
        #self.keyPressEvent = self.KeyPressEvent
        pass
    
    def KeyPressEvent(self, e: QKeyEvent | None) -> None:
        if e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_Space:
            self.autoCompleteFromAll()
        else:
            return super().keyPressEvent(e)
    
    def CursorPositionChanged(self, line : int, index : int) -> None:
        if self.isPythonFile:
            self.autoCompleter.GetCompletion(line + 1, index, self.text())
        pass
    
    def LoadedAutoCompleter(self):
        pass