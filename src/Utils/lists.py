from os.path import exists, join, dirname
from os import listdir
from .loggin import log

def read_wordlist(path):
    if not path:
        return log.critical("No argument was provided to load the Wordlist")
    elif not "/" in path:
        return [path]
    elif not exists(path):
        return log.critical(f"The Wordlist {path} doesn't exists")
    with open(path, 'r') as file:
        lines = file.read().split("\n")
        return lines

def read_header_file(path):
    if not path:
        return None
    elif not exists(path):
        return log.critical(f"The Header {path} doesn't exists")
    json = {}
    with open(path, "r") as file:
        lines = file.read().split("\n")
        for line in lines:
            splitted = line.replace(" ", "").split(": ")
            key = splitted[0]
            value = splitted[1]
            json[key] = value
        return json

def read_all_storage():
    path = join(dirname(__file__), "..", "Storages")
    return listdir(path)

def choice(files):
    try:
        index = int(log.input("Choose the target to attack> "))
        return files[index - 1].replace(".json", "")
    except (IndexError, ValueError) as e:
        if type(e).__name__ == 'IndexError':
            log.error(f"The index {e} wasn't found. Look at the table and type the correct Index")
        choice(files)

def make_question():
    files = read_all_storage()

    for i, f in enumerate(files):
        print(f"{f} ({i + 1})")

    return choice(files)




