from os.path import exists
from .hadler import CommandHandler
import readline

class Cerberus(CommandHandler):
    def __init__(self, cache: bool = True):
        super().__init__()
        self.load()
        if cache:
            self.log_file = ".cache/.log/.commands"
            self.history()
        
    def history(self) -> any:
        if not exists(self.log_file):
            with open(self.log_file, "w"):
                pass
        readline.read_history_file(self.log_file)
    
    def save(self) -> None:
        readline.write_history_file(self.log_file)
    
    def execute(self, line: str) -> bool:
        lines = line.split(" ")
        command = lines[0]
        args = lines[1:]

        self.save()
        self.e(command, args)
    
    def start(self):
        while True:
            line = input("\033[4mcerberus\033[0m > ")
            if line:
                self.execute(line)