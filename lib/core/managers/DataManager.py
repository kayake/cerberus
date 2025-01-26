import time
import json

class Cache:
    def __init__(self, __init__=None, ttl=False, ttl_timeout=0):
        self.cache = __init__ or {}
        if ttl:
            time.sleep(ttl_timeout)
            self.cache = {}
        
    @property
    def keys(self) -> list:
        return list(self.cache.keys())
    
    @property
    def values(self) -> list:
        return list(self.cache.values())
    
    def set(self, key, value):
        self.cache[key] = value

    def get(self, key:str) -> (str | int | object | list) | None:
        try:
            return self.cache[key]
        except KeyError:
            return None
    
    def remove(self, key):
        del self.cache[key]

    def getAll(self):
        return self.cache
    
    def forEach(self, function):
        for key, i in self.cache.items():
            function(key, i)

class SaveDataBase:
    def __init__(self, name):
        self.file = name
        self.path = f".cache/saves/{name}.json"

    def read(self) -> object | None:
        try:
            with open(self.path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return None
    
    def write(self, data: any) -> None:
        with open(self.path, "w") as file:
            json.dumps(data, file)
    
    def update(self, key, value) -> None:
        data = self.read()

        data[str(key)] = str(value)

        self.write(data)

