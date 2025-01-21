import time

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