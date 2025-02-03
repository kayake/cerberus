from .hadler import CommandHandler
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory, FileHistory
from prompt_toolkit.formatted_text import ANSI
from lib.core.loggin import log
from pathlib import Path
class Cerberus(CommandHandler):
    def __init__(self, cache: bool = True):
        super().__init__(cache=cache)
        self.__cache__ = cache
        if not cache:
            self.history = InMemoryHistory()
        else:
            path = Path.cwd() / ".cache/logs/.commands"
            path.touch()
            self.history = FileHistory(".cache/logs/.command")
        self.session = PromptSession(history=self.history)
        self.load()
        
    def execute(self, line: str) -> bool:
        lines = line.split(" ")
        command = lines[0]
        args = lines[1:]

        try:
            self.e(command, args)
        except Exception as e:
            log.error(f"(\033[1;35m{command}\033[0m \033[31m+\033[0m \033[1;34m{args}\033[0m) => {str(e)}")
    
    def start(self):
        while True:
            line = self.session.prompt(ANSI("\033[4mcerberus\033[0m > "))
            if line:
                self.execute(line)