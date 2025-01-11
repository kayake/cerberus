import time

class Cache:
    def __init__(self, __init__, ttl=False, ttl_timeout=0):
        self.cache = __init__ or {}
        if ttl:
            time.sleep(ttl_timeout)
            self.cache = {}
    
    def set(self, key, value):
        self.cache[key] = value

    def get(self, key):
        return self.cache[key]
    
    def remove(self, key):
        del self.cache[key]

    def getAll(self):
        return self.cache
    
    def forEach(self, function):
        for key, i in self.cache.items():
            function(key, i)


from tinydb import TinyDB
from os.path import join, dirname

class JSONDataBase:
    def __init__(self, path = "../Storages/"):
        self.path = f"{dirname(__file__)}/{path}"
    
    def load(self, name):
        if not name:
            return
        db_path = join(self.path, f'{name.lower()}.json')