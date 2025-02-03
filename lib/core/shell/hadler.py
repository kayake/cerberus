import importlib
import os

from lib.core.managers.DataManager import Cache
from lib.core.loggin import log
class CommandHandler:
    def __init__(self, cache: bool = True, path="lib.core.shell.commands"):
        self.__cache__ = cache
        self.path = path
        self.commands = Cache()
        self.aliases = Cache()

    def load(self) -> None:
            for filename in os.listdir(self.path.replace(".", "/")):
                if not filename.endswith(".py") or filename == "__init__.py":
                    return
                try:
                    module = importlib.import_module(f"{self.path}.{filename[:-3]}")

                    class_name = filename[:-3].capitalize()
                    command_class = getattr(module, class_name, None)
                    if command_class:
                        command_class = command_class(self)
                        self.commands.set(command_class.name, command_class)
                        if len(command_class.aliases) != 0:
                            for aliase in command_class.aliases:
                                self.aliases.set(aliase, command_class)
                except Exception as e:
                    log.error(f"(\033[1;35m{filename}\033[0m) => {str(e)}")
    
    def e(self, name:str, arguments:list) -> None:
        if not name:
            return
        command = self.commands.get(name) or self.aliases.get(name)
        if not command:
            cmd = f"{name} {"".join(arguments)}"
            log.debug(f"Command executed: {cmd}")
            return os.system(cmd)
        try:
            return command.run(arguments)
        except SystemExit:
            pass