import json
from typing import (Optional)
import os
from ..Utils.cache import Cache
from ..Utils.loggin import log
from ..Utils.database import db


cache = Cache(initial_values={
               "target": None,
               "control_port": 9051,
               "threads": 15,
               "timeout": 0,
               "attempts": 0
            })

from src.Utils.attack import threads

commands = ['set', 'options', 'run', 'init']

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
    cache.set("target", target.split("/")[2])
    return log.info(f"Request body found:\n{json.dumps(database.all())}", extra={"bold": True})

def set(args):
    return cache.set(key=args[0], value=args[1])

def options(args):
    print(f"\n{"=" * 70}")
    cache.forEach(organize)
    print(f"{"=" * 70}\n")

def run(args):
    if not args:
        return log.critical(f"Provide the Passwords Wordlist and Password or Usernames Wordlist or Username")
    sure = log.input(f"Username List or Username: {args[0]}\nPassword List or Password: {args[1]}\n\n> Are you sure about that? [Y/n] ") or 'y'
    if 'y' in sure.lower():
        threads(users=args[0], passd=args[1])
    else:
        what_to_change = log.input("Usernames - 2\nPassword - 1\nBoth - 3\n\n> What do you want to change? (1, 2 or 3): ").lower()
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


cmd = {
    "init": init,
    "options": options,
    "run": run,
}

class Shell:
    def __init__(self, verbose: Optional[bool] = False):
        self.verbose = verbose
        self.makeLoop()

    def exec(self, command):
       _command = command.split(" ")
       if _command[0] not in commands:
           log.debug(f"Command executed {command}\n")
           return os.system(command)
       else:
           return cmd[_command[0]](_command[1:])

    def makeLoop(self):
        exited = True
        while exited:
            command = input("cerberus> ")
            self.exec(command)