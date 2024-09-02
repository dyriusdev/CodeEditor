from PyQt5.QtCore import QObject, QThread
from PyQt5.Qsci import QsciAPIs
from jedi import Script
from jedi.api import Completion

class AutoComplete(QThread):

    def __init__(self, filePath : str, api : QsciAPIs) -> None:
        super(AutoComplete, self).__init__(None)
        self.filePath : QsciAPIs = filePath
        self.script : Script = None
        self.api : QsciAPIs = api
        self.completions : list[Completion] = None
        
        self.line : int = 0
        self.index : int = 0
        self.text : str = ""
        pass
    
    def run(self) -> None:
        try:
            self.script = Script(self.text, path=self.filePath)
            self.completions = self.script.complete(self.line, self.index)
            self.LoadAutoComplete(self.completions)
        except Exception as e:
            print(e)
        self.finished.emit()
        pass
    
    def LoadAutoComplete(self, completions : list[Completion]) -> None:
        self.api.clear()
        (self.api.add(i.name) for i in completions)
        self.api.prepare()
        pass
    
    def GetCompletion(self, line : int, index : int, text : str):
        self.line = line
        self.index = index
        self.text = text
        self.start()
        pass