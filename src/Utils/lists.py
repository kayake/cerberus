import os.path
import logging

log = logging.getLogger("cerberus")

def read_wordlist(path):
    if not path:
        return log.critical("No argument was provided to load the Wordlist")
    elif not "/" in path:
        return [path]
    elif not os.path.exists(path):
        return log.critical(f"The Wordlist {path} doesn't exists")
    with open(path, 'r') as file:
        lines = file.read().split("\n")
        return lines

def read_header_file(path):
    if not path:
        return None
    elif not os.path.exists(path):
        return log.critical(f"The Header {path} doesn't exists")
    json = {}
    with open(path, "r") as file:
        lines = file.read().split("\n")
        for line in lines:
            key = line.split(": ")[0]
            value = line.split(": ")[1]
            json[key] = value
        return json

