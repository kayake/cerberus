from json import dumps, loads, JSONDecodeError
from typing import (Optional)
from os import listdir, system
from os.path import join, dirname, exists

from tinydb import Query

from ..utils.cache import Cache
from ..utils.loggin import log
from ..utils.database import db
from src.utils.attack import Threads


cache = Cache(initial_values={
               "target": None,
               "control_port": 9051,
               "threads": 15,
               "timeout": 0,
               "attempts": 0
            })


commands = ['options', 'run', 'init', 'edit']

def organize(key, _):
    print(f'{key} - {cache.get(key)}')

def init(args=None):
    target = log.input("Target> ")
    database = db(args[0] if args else target.split("/")[2])
    if not database:
        data = log.input("Data Payload> ")
        headers_path = log.input("Headers Path (None)> ") or None
        method = log.input("Method (POST)> ") or "POST"
        success = log.input("Success response> ")
        fail = None
        if not success:
            fail = log.input("Fail response (401)> ") or 401

        database.insert({
            "url": target,
            "data": data,
            "headers": headers_path,
            "method": method,
            "success": success,
            "fail": fail
        })

        log.info(f"The Request Body was found at '{args[0] if args else target.split("/")[2]}.json'", extra={"bold": True})
    return log.info(f"Request body found:\n{dumps(database.all())}", extra={"bold": True})

def options(args):
    print(f"\n{"=" * 70}")
    for file in listdir(join(dirname(__file__), "..", "Storages")):
        print(file.replace(".json", ""))
    print(f"{"=" * 70}\n")

def run(args):
    if not args:
        return log.critical(f"Provide the Passwords Wordlist and Password or Usernames Wordlist or Username")
    target = None
    if len(args) == 3:
        target = args[2]
    sure = log.input(f"Username: {args[0]}\nPassword List or Password: {args[1]}\nTarget - {target} (Optional) (None)\n\n> Are you sure about that? [Y/n] ") or 'y'
    if 'y' in sure.lower():
        Threads(username=args[0], path_password=args[1], target=target)
    else:
        what_to_change = log.input("Password - 1\nUsernames - 2\nBoth - 3\n\n> What do you want to change? (1, 2 or 3): ").lower()
        if 'p' in what_to_change or '1' in what_to_change:
            value = log.input(f"Password - {args[1]}\n\nNew password payload> ")
            run([args[0], value])
        elif 'u' in what_to_change or '2' in what_to_change:
            value = log.input(f"Usernames - {args[0]}\n\nNew username payload> ")
            run([value, args[1]])
        elif 'b' in what_to_change or '3' in what_to_change:
            passd = log.input(f"Password - {args[1]}\n\nNew password payload> ")
            user = log.input(f"Usernames - {args[0]}\n\nNew username payload> ")
            run([user, passd])

def edit(args):
    if not args or not args[0]:
        log.error("Provide a file name to edit (e.g: edit google.com)")
        return options(None)
    if not exists(join(dirname(__file__), "..", "Storages", f"{args[0]}.json")):
        log.error(f"The file {args[0]} doesn't exists")
        return options(None)
    Editor(args[0])

cmd = {
    "init": init,
    "options": options,
    "run": run,
    "edit": edit
}

class Shell:
    def __init__(self, verbose: Optional[bool] = False):
        self.verbose = verbose
        self.makeLoop()

    def exec(self, command):
       _command = command.split(" ")
       if _command[0] not in commands:
           log.debug(f"Command executed {command}\n")
           return system(command)
       else:
           return cmd[_command[0]](_command[1:])

    def makeLoop(self):
        exited = True
        while exited:
            command = input("\033[4mcerberus\033[0m > ")
            if command:
                self.exec(command)


class Editor:
    SUB_COMMANDS = ["ed", "del", "delall", "edall"]
    def __init__(self, name):
        self.database = db(name)
        self.name = name
        self.data = self.database.all()[0]
        self.url = self.data['url']
        self.exited = False
        self.__select__()

    def __input__(self):
        lines = input(f"\033[4mcerberus\033[0m editor(\033[1m\033[38;2;255;0;0mstorages/{self.name}.json\033[0m) > ").split(" ")
        if not lines[0]:
            return
        sub_command = lines[0]
        arguments = lines[1:]
        match sub_command:
            case 'ed':
                return self.edit(arguments)
            case 'edall':
                return self.edit_all(arguments)
            case 'del':
                return self.delete(arguments)
            case 'delall':
                return self.delete_all()
            case 'exit':
                self.exited = True
                return
            case _:
                return log.error(f"The command {sub_command} doesn't exists")

    def __select__(self):
        while not self.exited:
            self.__input__()

    def __print_keys__(self):
        for k,v in self.data.items():
            print(f"{k}: {v or 'None'}")

    def __update__(self, key, value):
        K = Query()
        self.database.update({ key: value }, K.url == self.url)
        self.data = self.database.all()
        log.info(f"Updated '{key}' to '{value}':\n{self.data}")

    def __delete_and_update__(self, new_object):
        self.database.truncate()
        try:
            self.database.insert(loads(new_object))
            self.data = self.database.all()
            log.info(f"Substituted {self.name}'s data to {new_object} ")
        except JSONDecodeError as e:
            return log.critical(f"Could not add this object due to format error: {e}")

    def __delete_all__(self):
       self.database.truncate()
       self.data = None

    def __delete_key__(self, key):
        self.__update__(key, None)

    def __edit__(self, key, value):
        yn = log.input(f"{key} - {value}\n\nAre you sure about that? [Y/n] ") or 'y'
        if 'y' not in yn.lower():
            return log.info("Cancelling edition. Try edit again")
        try:
            self.__update__(key, value)
        except (KeyError, ValueError) as e:
            if type(e).__name__ == "ValueError":
                self.__update__(key, value)
            else:
                return log.error(f"The mentioned key doesn't exists")

    def delete(self, arg):
        if not arg:
            self.__print_keys__()
            key = log.input("\n\nWitch key do you want to edit? ")
            if not key:
                return log.info("Aborting...")
            self.__delete_key__(key)
        self.__delete_key__(arg[0])

    def delete_all(self):
        log.warning("You are about to delete all datas")
        yn = log.input(f"\rAre you do you want to delete all datas of {self.name}? [Y/n] ") or 'n'
        if not 'y' in yn.lower():
            return log.info("Aborting...")
        self.__delete_all__()

    def edit(self, args):
        if len(args) == 0:
            self.__print_keys__()
            key = log.input("\n\nWitch key do you want to edit? ")
            if not key:
                return log.info("Aborting...")
            value = log.input("\n\nWhat value do you want to change? ")
            return self.__edit__(key, value)
        elif len(args) == 1:
            return log.critical("Provide a key and a value to edit (e.g: edit success 401)")
        else:
            self.__edit__(args[0], args[1])

    def edit_all(self, arg):
        if not arg:
            return log.critical(f"Provide a object to substitute {self.data}")
        self.__delete_and_update__(arg[0])