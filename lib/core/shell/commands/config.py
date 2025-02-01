import argparse
from lib.core.managers.config import ConfigManager

class Config:
    name = "config"
    aliases = ["conf", "edit", "change", "cf"]
    description = "Configure your configuration file"
    def __init__(self, this):
        self.cache = this

        self.parser = argparse.ArgumentParser(prog="config", description="Edit configuration file.")

        g1 = self.parser.add_argument_group(title="Configuration", description="Edit the file configuration.")
        g1.add_argument("--set", "-S", type=list, help="Set or update a new value of the configuration file.", required=False)
        g1.add_argument("--delete", "-D", type=str, help="Delete some information.", required=False)
        g1.add_argument("--get", "-g", type=str, help="Get some information in configuration file.", required=False)
        g1.add_argument("--get-all", "-G", action="store_true", help="Get all information in configuration file.", required=False)
        
        g2 = self.parser.add_argument_group(title="Customization", description="Customize your configuration file.")
        g2.add_argument("--file", "-F", type=str, help="Change your configuration file.", default="config.yaml", required=False)

    
    def run(self, arguments):
        if not arguments:
            return self.parser.print_help()
        arguments=self.parser.parse_args(arguments)
        config = ConfigManager(arguments.file)

        if arguments.set:
            config.set(arguments.set[0], arguments.set[1])
        elif arguments.delete:
           config.delete(arguments.delete, None)
        elif arguments.get:
            print(config.get(arguments.get))
        elif arguments.get_all:
            json = config.config
            for k, v in json.items():
                print(f"{k}: {v}")