import importlib
import importlib.util
from pathlib import Path
from lib.core.loggin import log

class Plugin_Handler:
    def __init__(self):
        self.plugins = {}

    def load_plugin(self, name: str) -> None:
        path = Path(name)

        if not path.exists():
            return log.error(f"Plugin {name} not found")
        
        module_name = f"plugin_{path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for name, obj in module.__dict__.items():
            if isinstance(obj, type):
                relative_path = path.relative_to("lib/plugins")
                self.plugins[str(relative_path)] = obj

    def load_all_plugins(self) -> None:
        base = Path("lib/plugins")

        for file in base.glob("**/*.py"):
            if file.is_file():
                try:
                    self.load_plugin(file)
                except Exception as e:
                    log.error(f"(\033[1;35m{file}\033[0m) => {str(e)}")

    def execute_plugin(self, name: str, arguments: list | tuple) -> None:
        if name not in self.plugins:
            return log.error(f"Plugin {name} not found")
        
        plugin_class = self.plugins[name]
        plugin_instance = plugin_class()
        plugin_instance.run(arguments)

    def list(self) -> object:
        return self.plugins

class Plugin(Plugin_Handler):
    name = "plugin"
    aliases = ["plugs", "plug", "plugins", "pl", "p"]
    description = "Use any plugins in /lib/plugins/"

    def __init__(self, this):
        self.this = this
        log.debug("Loading plugins...")

        super().__init__()


        self.load_all_plugins()

    def run(self, arguments):
        if not arguments:
            return print(f"\nplugin use - Use a plugin\nplugin list - List all plugins registred\n")
        
        if arguments[0] == "use":

            if len(arguments) == 1:
                return log.error("Provide a plugin to use")

            plugin = arguments[1]

            if not plugin:
                return log.error("Provide a plugin to use")

            self.execute_plugin(plugin, self.this)
        
        elif arguments[0] == "list":
            list_ = self.list()
            if not list_:
                return log.error("No plugins was detected")
            print("="*50)
            for name, value in list_.items():
                print(f"{name} - {value.description}")
            print("="*50)