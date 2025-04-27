from prompt_toolkit.formatted_text import ANSI
from lib.core.plugins import PluginHandler
import logging
log = logging.getLogger(__name__)

class Plugin(PluginHandler):
    def run(self, arguments) -> None:
        if arguments.list:
            for k, v in self.plugins.items():
                print(f"{k} - {v}")
            return
        if arguments.use:
            if arguments.use not in self.plugins:
                return log.error(f"BOLDPlugin {arguments.use} not found")
            plugin_class = self.plugins[arguments.use]
            plugin_instance = plugin_class(self)
            plugin_instance.run(arguments.arguments)
            return
        if arguments.load:
            self.load_plugin(arguments.load)
            return