import argparse

class Help:
    name = "help"
    aliases = ["?"]
    description = "It helps you"
    def __init__(self, this):
        self.this = this
        self.parser = argparse.ArgumentParser(prog="help", epilog="help ---name attack", )
        self.parser.add_argument("--name", "-n", "-N", type=str, help="Find a specific command", required=False)
        
    
    def run(self, arguments):
        if arguments:
            arguments = self.parser.parse_args(arguments)
            if arguments.name:
                command = self.this.commands.get(arguments.name) or self.this.aliases.get(arguments.name)
                aliases_string = ", ".join(command.aliases)
                return print(f"\nName: {command.name}\nDescription: {command.description}\nAliases: {aliases_string}\n")
        else:
            print()
            for command, value in self.this.commands.cache.items():
                print(f"{command} - {value.description}")
            print()