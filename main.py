from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import requests, random

app = FastAPI()
app.mount("/", StaticFiles(directory="static", html=True), name="static")

EDU_STREAM_API_BASE_URL = "https://siawaseok.duckdns.org/api/stream/"
EDU_VIDEO_API_BASE_URL = "https://siawaseok.duckdns.org/api/video2/"
STREAM_YTDL_API_BASE_URL = "https://yudlp.vercel.app/stream/"
SHORT_STREAM_API_BASE_URL = "https://yt-dl-kappa.vercel.app/short/"

INVIDIOUS_SEARCH = "https://api-five-zeta-55.vercel.app/search"
INVIDIOUS_COMMENTS = [
    "https://invidious.lunivers.trade/",
    "https://iv.melmac.space/",
    "https://iv.duti.dev/",
]

def pick(lst): return random.choice(lst)

@app.get("/api/search")
def search(q: str):
    r = requests.get(INVIDIOUS_SEARCH, params={"q": q, "type": "video"})
    return r.json() if r.ok else []

@app.get("/api/watch/{vid}")
def watch(vid: str):
    comments_api = pick(INVIDIOUS_COMMENTS)
    comments = requests.get(f"{comments_api}api/v1/comments/{vid}").json()
    return {
        "streams": {
            "edu": EDU_STREAM_API_BASE_URL + vid,
            "high": EDU_VIDEO_API_BASE_URL + vid,
            "ytdl": STREAM_YTDL_API_BASE_URL + vid,
            "short": SHORT_STREAM_API_BASE_URL + vid
        },
        "comments": comments.get("comments", [])
    }
