import argparse

class Help:
    name = "help"
    aliases = ["h", "?"]
    description = "Display this help message"
    def __init__(self, this):
        self.cache = this
        self.parser = argparse.ArgumentParser(prog="help", epilog="help attack", )
        self.parser.add_argument("--command", "-c", "--name", "-n", type=str, help="Command to display help for (e.g: help --command attack)", required=False)
    
    def run(self, arguments) -> None:
        if not arguments:
            for k, v in self.cache.commands.items():
                print(f"{k} - {v.description}")
            return
        arguments = self.parser.parse_args(arguments)
        command = self.cache.commands.get(arguments.command) or self.cache.aliases.get(arguments.command)
        if not command:
            return print(f"Command {arguments.command} not found")
        print(command.parser.print_help())
        return