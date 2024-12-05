class Cache:
    def __init__(self, initial_values = {}):
        self.cache = initial_values

    def set(self, key, value):
        self.cache[key] = value
        return self.get(key)

    def get(self, key):
        return self.cache[key]

    def remove(self, key):
        del self.cache[key]

    def getAll(self):
        return self.cache

    def forEach(self, fn):
        for key, i in self.cache.items():
            fn(key, i)
