import random
import time
from iwashi_tube.cache import cache

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
    instances = INSTANCES.get(kind, []).copy()
    random.shuffle(instances)

    last_error = None

    for instance in instances[:MAX_RETRY]:
        dead_key = f"dead:{kind}:{instance}"
        if cache.get(dead_key):
            continue

        try:
            return func(instance)
        except Exception as e:
            last_error = e
            cache.set(dead_key, True, ttl=90)
            time.sleep(0.3)

    print(f"[{kind}] all instances failed:", last_error)
    return None
