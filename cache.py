import time

_store = {}

def get(key):
    item = _store.get(key)
    if not item:
        return None
    value, exp = item
    if exp < time.time():
        del _store[key]
        return None
    return value

def set(key, value, ttl=60):
    _store[key] = (value, time.time() + ttl)
