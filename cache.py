import time
from threading import Lock

class TTLCache:
    def __init__(self):
        self.store = {}
        self.lock = Lock()

    def get(self, key):
        with self.lock:
            item = self.store.get(key)
            if not item:
                return None
            value, expire = item
            if expire < time.time():
                del self.store[key]
                return None
            return value

    def set(self, key, value, ttl=60):
        with self.lock:
            self.store[key] = (value, time.time() + ttl)

cache = TTLCache()
