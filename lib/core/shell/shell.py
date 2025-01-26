from .hadler import CommandHandler
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory, FileHistory
from prompt_toolkit.formatted_text import ANSI
class Cerberus(CommandHandler):
    def __init__(self, cache: bool = True):
        super().__init__()
        if not cache:
            self.history = InMemoryHistory()
        else:
            self.history = FileHistory(".cache/logs/.command")
        self.session = PromptSession(history=self.history)
        self.load()
        
    def execute(self, line: str) -> bool:
        lines = line.split(" ")
        command = lines[0]
        args = lines[1:]

        self.e(command, args)
    
    def start(self):
        while True:
            line = self.session.prompt(ANSI("\033[4mcerberus\033[0m > "))
            if line:
                self.execute(line)