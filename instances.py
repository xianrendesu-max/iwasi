import random
import time
import cache

INSTANCES = {
    "playlist": [
        "https://invidious.lunivers.trade",
        "https://invidious.ducks.party",
        "https://super8.absturztau.be",
        "https://invidious.nikkosphere.com",
        "https://yt.omada.cafe",
        "https://iv.melmac.space",
        "https://iv.duti.dev",
    ],
    "search": [
        "https://api-five-zeta-55.vercel.app",
    ],
    "channel": [
        "https://invidious.lunivers.trade",
        "https://invid-api.poketube.fun",
        "https://invidious.ducks.party",
        "https://super8.absturztau.be",
        "https://invidious.nikkosphere.com",
        "https://yt.omada.cafe",
        "https://iv.melmac.space",
        "https://iv.duti.dev",
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

MAX_RETRY = 3


def try_instances(kind: str, func):
    pool = INSTANCES.get(kind, []).copy()
    random.shuffle(pool)

    for instance in pool[:MAX_RETRY]:
        key = f"dead:{kind}:{instance}"
        if cache.get(key):
            continue
        try:
            return func(instance)
        except:
            cache.set(key, True, ttl=90)
            time.sleep(0.3)
    return None
