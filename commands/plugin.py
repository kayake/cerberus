from prompt_toolkit.formatted_text import ANSI
from lib.core.plugins import PluginHandler
import logging
log = logging.getLogger(__name__)

class Plugin(PluginHandler):
    def run(self, arguments) -> None:
        if not arguments:
            return print(self.parser.print_help())
        arguments = self.parser.parse_args(arguments)
        if arguments.list:
            for k, v in self.plugins.items():
                print(f"{k} - {v}")
            return
        if arguments.use:
            if arguments.use not in self.plugins:
                return log.error(f"BOLDPlugin {arguments.use} not found")
            plugin_class = self.plugins[arguments.use]
            plugin_instance = plugin_class(self)
            while True:
                i = self.this.session.prompt(ANSI(f"\033[4mcerberus\033[0m {arguments.use.split("/")[0]}(\033[1;31m{arguments.use}\033[0m) > "))
                if i == "exit":
                    break
                plugin_instance.run(i)
            return
        if arguments.load:
            self.load_plugin(arguments.load)
            return