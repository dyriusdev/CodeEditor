from PyQt5.Qsci import QsciLexerCustom, QsciScintilla
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import keyword
import types
import builtins
import re



class PyCustomLexer(QsciLexerCustom):
    
    def __init__(self, parent : QObject | types.NoneType = ...) -> types.NoneType:
        super(PyCustomLexer, self).__init__(parent)
        
        # Default settings
        self.color1 = "#abb2bf"
        self.color2 = "#282c34"
        self.setDefaultColor(QColor(self.color1))
        self.setDefaultPaper(QColor(self.color2))
        self.setDefaultFont(QFont("Consolas", 14))
        
        self.KEYWORD_LIST = keyword.kwlist
        self.builtinFunctionsNames = [name for name, obj in vars(builtins).items() if isinstance(obj, types.BuiltinFunctionType)]

        self.DEFAULT = 0
        self.KEYWORD = 1
        self.TYPES = 2
        self.STRING = 3
        self.KEYARGS = 4
        self.BRACKETS = 5
        self.COMMENTS = 6
        self.CONSTANTS = 7
        self.FUNCTIONS = 8
        self.CLASSES = 9
        self.FUNCTION_DEF = 10
        
        self.setColor(QColor(self.color1), self.DEFAULT)
        self.setColor(QColor("#c678dd"), self.KEYWORD)
        self.setColor(QColor("#56b6c2"), self.TYPES)
        self.setColor(QColor("#98c379"), self.STRING)
        self.setColor(QColor("#c678dd"), self.KEYARGS)
        self.setColor(QColor("#c678dd"), self.BRACKETS)
        self.setColor(QColor("#777777"), self.COMMENTS)
        self.setColor(QColor("#d19a5e"), self.CONSTANTS)
        self.setColor(QColor("#61afd1"), self.FUNCTIONS)
        self.setColor(QColor("#C68F55"), self.CLASSES)
        self.setColor(QColor("#61afd1"), self.FUNCTION_DEF)

        self.setPaper(QColor(self.color2), self.DEFAULT)
        self.setPaper(QColor(self.color2), self.KEYWORD)
        self.setPaper(QColor(self.color2), self.TYPES)
        self.setPaper(QColor(self.color2), self.STRING)
        self.setPaper(QColor(self.color2), self.KEYARGS)
        self.setPaper(QColor(self.color2), self.BRACKETS)
        self.setPaper(QColor(self.color2), self.COMMENTS)
        self.setPaper(QColor(self.color2), self.CONSTANTS)
        self.setPaper(QColor(self.color2), self.FUNCTIONS)
        self.setPaper(QColor(self.color2), self.CLASSES)
        self.setPaper(QColor(self.color2), self.FUNCTION_DEF)

        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.DEFAULT)
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.KEYWORD)
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.CLASSES)
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.FUNCTION_DEF)
        pass
    
    def language(self) -> str:
        return "PyCustomLexer"
    
    def description(self, style : int) -> str:
        match style:
            case self.DEFAULT:
                return "DEFAULT"
            case self.KEYWORD:
                return "KEYWORD"
            case self.TYPES:
                return "TYPES"
            case self.STRING:
                return "STRING"
            case self.KEYARGS:
                return "KEYARGS"
            case self.BRACKETS:
                return "BRACKETS"
            case self.COMMENTS:
                return "COMMENTS"
            case self.CONSTANTS:
                return "CONSTANTS"
            case self.FUNCTIONS:
                return "FUNCTIONS"
            case self.CLASSES:
                return "CLASSES"
            case self.FUNCTION_DEF:
                return "FUNCTION_DEF"
        return ""
    
    def styleText(self, start : int, end : int) -> types.NoneType:
        self.startStyling(start)
        editor : QsciScintilla = self.parent()
        text : str = editor.text()[start:end]
        
        tokenList = self.GetTokens(text)
        stringFlag : bool = False
        
        def GetNextToken(skip : int = None):
            if len(tokenList) > 0:
                if skip is not None and skip != 0:
                    for _ in range(skip - 1):
                        if len(tokenList) > 0:
                            tokenList.pop(0)
                return tokenList.pop(0)
            else:
                return None
        
        def PeekToken(n : int = 0):
            try:
                return tokenList[n]
            except IndexError:
                return [""]
        
        def SkipSpacePeek(skip = None):
            i = 0
            token = (" ")
            if skip is not None:
                i = skip
            while token[0].isspace():
                token = PeekToken(i)
                i += 1
            return token, i
        
        while True:
            currentToken = GetNextToken()
            if currentToken is None:
                break
            token : str = currentToken[0]
            tokenLen : int = currentToken[1]
            
            if stringFlag:
                self.setStyling(tokenLen, self.STRING)
                if token == '"' or token == "'":
                    stringFlag = False
                continue  
            
            if token == "class":
                name, ni = SkipSpacePeek()
                bracOrColon, _ = SkipSpacePeek(ni)
                if name[0].isidentifier() and bracOrColon[0] in (":", "("):
                    self.setStyling(tokenLen, self.KEYWORD)
                    _ = SkipSpacePeek(ni)
                    self.setStyling(name[1] + 1, self.CLASSES)
                    continue
                else:
                    self.setStyling(tokenLen, self.KEYWORD)
                    continue
            elif token == "def":
                name, ni = SkipSpacePeek()
                if name[0].isidentifier():
                    self.setStyling(tokenLen, self.KEYWORD)
                    _ = GetNextToken(ni)
                    self.setStyling(name[1] + 1, self.FUNCTION_DEF)
                    continue
                else:
                    self.setStyling(tokenLen, self.KEYWORD)
            elif token in self.KEYWORD_LIST:
                self.setStyling(tokenLen, self.KEYWORD)
            elif token.isnumeric() or token == "self":
                self.setStyling(tokenLen, self.CONSTANTS)
            elif token in ["(", ")", "[", "]", "{", "}"]:
                self.setStyling(tokenLen, self.BRACKETS)
            elif token == '"' or token == "'":
                self.setStyling(tokenLen, self.STRING)
                stringFlag = True
            elif token in self.builtinFunctionsNames or token in ["+", "-", "*", "/", "%", "=", "<", ">"]:
                self.setStyling(tokenLen, self.TYPES)
            else:
                self.setStyling(tokenLen, self.DEFAULT)
        pass
    
    def GetTokens(self, text : str) -> list[str, int]:
        p = re.compile(r"[*]\/|\/[*]\s+|\w+|\W")
        return [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]