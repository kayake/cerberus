import importlib
import importlib.util
from pathlib import Path
import logging

log = logging.getLogger(__name__)

class PluginHandler:
    def __init__(self, this):
        """
        Initializes the plugin handler.
        
        :param this: Main instance containing the session.
        """
        self.plugins = {}
        self.this = this

    def load_plugin(self, name: str) -> None:
        """
        Loads a plugin from a file path.

        :param name: File path of the plugin.
        """
        path = Path(name)

        if not path.exists():
            log.error(f"Plugin {name} not found")
            return
        
        module_name = f"plugin_{path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for obj_name, obj in module.__dict__.items():
            if isinstance(obj, type):
                relative_path = path.relative_to("lib/plugins")
                self.plugins[str(relative_path)] = obj

    def load_all_plugins(self) -> None:
        """
        Loads all plugins from the 'lib/plugins' directory.
        """
        base = Path("lib/plugins")

        for file in base.glob("**/*.py"):
            if file.is_file():
                try:
                    self.load_plugin(file)
                except Exception as e:
                    log.error(f"(\033[1;35m{file}\033[0m) => {str(e)}")

    def execute_plugin(self, name: str, arguments: list | tuple) -> None:
        """
        Executes a plugin with the provided arguments.

        :param name: Name of the plugin.
        :param arguments: List or tuple of arguments for the plugin.
        """
        if name not in self.plugins:
            log.error(f"Plugin {name} not found")
            return
        
        plugin_class = self.plugins[name]
        plugin_instance = plugin_class(self)
        plugin_instance.run(arguments)

    def list_plugins(self) -> dict:
        """
        Lists all loaded plugins.

        :return: Dictionary of loaded plugins.
        """
        return self.plugins