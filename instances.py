import random
import requests
from .cache import cache

INSTANCES = {
    "search": [
        "https://api-five-zeta-55.vercel.app",
    ],
    "comments": [
        "https://invidious.lunivers.trade",
        "https://invidious.ducks.party",
        "https://super8.absturztau.be",
        "https://invidious.nikkosphere.com",
        "https://yt.omada.cafe",
        "https://iv.duti.dev",
        "https://iv.melmac.space",
    ],
}

def try_instances(kind, path, params=None, timeout=4):
    key = f"{kind}:{path}:{params}"
    cached = cache.get(key)
    if cached:
        return cached

    for base in random.sample(INSTANCES[kind], len(INSTANCES[kind])):
        try:
            r = requests.get(
                f"{base}{path}",
                params=params,
                timeout=timeout
            )
            if r.status_code == 200:
                data = r.json()
                cache.set(key, data, ttl=60)
                return data
        except Exception:
            continue

    return None
