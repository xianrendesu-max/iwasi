import time

class SimpleCache:
    def __init__(self):
        self.store = {}

    def get(self, key):
        item = self.store.get(key)
        if not item:
            return None
        value, expire = item
        if expire and expire < time.time():
            del self.store[key]
            return None
        return value

    def set(self, key, value, ttl=60):
        expire = time.time() + ttl if ttl else None
        self.store[key] = (value, expire)


cache = SimpleCache()
