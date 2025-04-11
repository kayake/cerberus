import argparse
import os
import logging
import sys
from pathlib import Path
from lib.core import CustomFormatter
import asyncio

from lib.core import CheckUpdate

"""Importing commands"""
from commands.attack import Attack
from commands.plugin import Plugin

handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())

LEVELS = {
    "1": logging.WARNING,
    "2": logging.INFO,
    "3": logging.DEBUG,
    "4": 4,
    "5": 5,
    "6": 5,
    "7": 5
}

def check_update():
    updater: CheckUpdate = CheckUpdate()
    return updater.update()


async def main(arguments):
    try:
        if arguments.command == "attack":
            await Attack().run(arguments)
        elif arguments.command == "plugin":
            await Plugin().run(arguments)
    except KeyboardInterrupt:
        log.error("User interrupted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="cerberus", epilog="cerberus --verbose 3 attack -h")
    commands = parser.add_subparsers(dest="command", title="Commands")

    attack = commands.add_parser("attack", help="Start an attack (Consider executing python3 crbs.py attack -h for attack options)")
    # mode = attack.add_argument_group("Attack mode")
    request_group = attack.add_argument_group("Request options")
    request_group.add_argument("--tor", "-t", action="store_true", help="Use Tor", required=False)
    request_group.add_argument("--proxy", "-p", action="store_true", help="Use a proxy", required=False)
    request_group.add_argument("--proxies", "-ps", action="store_true", help="Use multiple proxies", required=False)
    request_group.add_argument("--random-agent", "-ra", action="store_true", help="Use a random user-agent", required=False)
    request_group.add_argument("--user-agent", "-ua", type=str, help="Specify a user-agent", required=False)
    request_group.add_argument("--user-agent-list", "-ual", type=str, help="Path to a list of user-agents", required=False)
    config_group = attack.add_argument_group("Configuration options")
    config_group.add_argument("--config", "-C", type=str, help="Path to the attack configuration file", required=False, default="configs/attack.yaml")
    config_group.add_argument("--output", "-o", type=str, help="Output file for found passwords", required=False)
    config_group.add_argument("--ignore", "-I", action="store_true", help="Ignore checkpoints", required=False)
    proccess_group = attack.add_argument_group("Process options")
    proccess_group.add_argument("--threads", "-T", type=int, help="Enable threads", required=False, default=10)
    proccess_group.add_argument("--clusters", "-c", type=int, help="Enable clusters", required=False, default=5)

    plugin = commands.add_parser("plugin", help="Use a plugin in 'lib/plugins/'")
    plugin.add_argument("--load", type=str, help="Load a plugin", required=False)
    plugin.add_argument("--list", action="store_true", help="List all loaded plugins", required=False)
    plugin.add_argument("--use", type=str, help="Execute a plugin", required=False)


    version = parser.add_argument_group("Version options")
    version.add_argument("--version", action="store_true", help="Show the version", required=False)
    update = parser.add_argument_group("Update options")
    update.add_argument("--update", "-u", action="store_true", help="Update Cerberus", required=False)
    others = parser.add_argument_group("Others")
    others.add_argument("--verbose", "-v", type=str, help="Set debug level", default="2", metavar="LEVEL", required=False)
    arguments= parser.parse_args()
    logging.basicConfig(level=LEVELS[arguments.verbose], handlers=[handler])

    log = logging.getLogger("crbs.py")

    version = "unknow"

    try:
        run_git, version, type = check_update()  # Check for updates in the background
    except Exception as e:
        log.error(f"Could not check update: {str(e)}")
        pass
    if arguments.version:
        print(f"Cerberus {version}")
        sys.exit()
    if arguments.update:
        log.info("Updating Cerberus...")
        os.system("git pull")
        log.info("Updated")
        sys.exit()
    try:
        asyncio.run(main(arguments=arguments))
    except KeyboardInterrupt as e:
        log.error("\nUser interrupted.")
        sys.exit(0)
    except Exception as e:
        log.error(f"\nAn error occurred: {str(e)}")
        sys.exit(1)
    finally:
        log.info("Exiting Cerberus.")
        sys.exit(0)