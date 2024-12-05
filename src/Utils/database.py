from tinydb import TinyDB
from os.path import join, dirname

def db(name):
    if not name:
        return
    db_path = join(dirname(__file__), '..', 'Storages', f'{name.lower()}.json')
    return TinyDB(db_path)