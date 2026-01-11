# ===============================
# Imports
# ===============================
import json, time, datetime, urllib.parse, requests, asyncio, concurrent.futures
from pathlib import Path
from typing import Union, List, Dict, Any

from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool

# ===============================
# Base / Template
# ===============================
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# ===============================
# App
# ===============================
app = FastAPI(title="🐟 イワシtube")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# ===============================
# Constants
# ===============================
MAX_API_WAIT = (3.0, 8.0)
MAX_TIME = 10.0
FAILED = "Load Failed"

EDU_STREAM_API_BASE_URL = "https://siawaseok.duckdns.org/api/stream/"
EDU_VIDEO_API_BASE_URL = "https://siawaseok.duckdns.org/api/video2/"
STREAM_YTDL_API_BASE_URL = "https://yudlp.vercel.app/stream/"
SHORT_STREAM_API_BASE_URL = "https://yt-dl-kappa.vercel.app/short/"
BBS_EXTERNAL_API_BASE_URL = "https://server-bbs.vercel.app"

# ===============================
# Invidious
# ===============================
INVIDIOUS = {
    "search": ["https://api-five-zeta-55.vercel.app/"],
    "playlist": [
        "https://invidious.lunivers.trade/",
        "https://invidious.ducks.party/",
        "https://iv.melmac.space/",
        "https://iv.duti.dev/"
    ],
    "channel": [
        "https://invidious.lunivers.trade/",
        "https://invid-api.poketube.fun/",
        "https://iv.melmac.space/"
    ],
    "comments": [
        "https://invidious.lunivers.trade/",
        "https://iv.melmac.space/"
    ]
}

# ===============================
# Utils
# ===============================
class APITimeoutError(Exception): ...

def ua():
    return {"User-Agent": "Mozilla/5.0"}

def is_json(t: str):
    try:
        json.loads(t)
        return True
    except:
        return False

def ytimg(v): 
    return f"https://i.ytimg.com/vi/{v}/hqdefault.jpg"

# ===============================
# Invidious request (race)
# ===============================
def request_api(path: str, apis: list[str]) -> str:
    with concurrent.futures.ThreadPoolExecutor(len(apis)) as ex:
        futures = {
            ex.submit(
                requests.get,
                api + "api/v1" + path,
                headers=ua(),
                timeout=MAX_API_WAIT
            ): api for api in apis
        }
        for f in concurrent.futures.as_completed(futures, timeout=MAX_TIME):
            try:
                r = f.result()
                if r.status_code == 200 and is_json(r.text):
                    return r.text
            except:
                pass
    raise APITimeoutError("All Invidious APIs failed")

# ===============================
# EDU Video
# ===============================
def fetch_edu_video(videoid: str):
    r = requests.get(
        EDU_VIDEO_API_BASE_URL + urllib.parse.quote(videoid),
        headers=ua(),
        timeout=MAX_API_WAIT
    )
    r.raise_for_status()
    return r.json()

async def get_video_data(videoid: str):
    t = await run_in_threadpool(fetch_edu_video, videoid)

    info = {
        "videoid": videoid,
        "title": t.get("title", FAILED),
        "author": t.get("author", {}).get("name", FAILED),
        "author_id": t.get("author", {}).get("id", ""),
        "views": t.get("views", 0),
        "likes": t.get("likes", 0),
        "published": t.get("relativeDate", ""),
        "description": t.get("description", {}).get("formatted", ""),
        "thumbnail": ytimg(videoid)
    }

    related = []
    for r in t.get("related", []):
        if r.get("videoId"):
            related.append({
                "id": r["videoId"],
                "title": r.get("title", FAILED),
                "author": r.get("channel", FAILED),
                "thumbnail": ytimg(r["videoId"])
            })

    return info, related

# ===============================
# Streams
# ===============================
def get_360p(videoid: str) -> str:
    r = requests.get(
        STREAM_YTDL_API_BASE_URL + videoid,
        headers=ua(),
        timeout=MAX_API_WAIT
    )
    r.raise_for_status()
    for f in r.json().get("formats", []):
        if f.get("itag") == "18":
            return f["url"]
    raise APITimeoutError("360p not found")

def get_best_m3u8(videoid: str) -> dict:
    r = requests.get(
        f"https://yudlp.vercel.app/m3u8/{videoid}",
        timeout=15
    )
    r.raise_for_status()
    fmts = r.json().get("m3u8_formats", [])
    fmts = sorted(fmts, key=lambda x: int(x.get("resolution", "0x0").split("x")[-1]), reverse=True)
    if not fmts:
        raise APITimeoutError("No m3u8")
    return {
        "url": fmts[0]["url"],
        "resolution": fmts[0]["resolution"]
    }

# ===============================
# Pages
# ===============================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = ""):
    results = []
    if q:
        data = await run_in_threadpool(
            request_api,
            f"/search?q={urllib.parse.quote(q)}&hl=jp",
            INVIDIOUS["search"]
        )
        for d in json.loads(data):
            if d.get("type") == "video":
                results.append({
                    "id": d["videoId"],
                    "title": d["title"],
                    "author": d["author"],
                    "thumbnail": ytimg(d["videoId"])
                })
    return templates.TemplateResponse(
        "search.html",
        {"request": request, "results": results, "q": q}
    )

@app.get("/watch/{videoid}", response_class=HTMLResponse)
async def watch(request: Request, videoid: str):
    info, related = await get_video_data(videoid)

    comments_raw = await run_in_threadpool(
        request_api,
        f"/comments/{videoid}",
        INVIDIOUS["comments"]
    )
    comments = [{
        "author": c["author"],
        "body": c["contentHtml"]
    } for c in json.loads(comments_raw).get("comments", [])]

    streams = {
        "high": f"/api/stream/high/{videoid}",
        "360p": f"/api/stream/360/{videoid}",
        "embed": f"/api/stream/edu/{videoid}"
    }

    return templates.TemplateResponse(
        "watch.html",
        {
            "request": request,
            "video": info,
            "related": related,
            "comments": comments,
            "streams": streams
        }
    )

# ===============================
# Stream APIs
# ===============================
@app.get("/api/stream/high/{videoid}")
async def api_high(videoid: str):
    d = await run_in_threadpool(get_best_m3u8, videoid)
    return {"url": d["url"], "resolution": d["resolution"]}

@app.get("/api/stream/360/{videoid}")
async def api_360(videoid: str):
    url = await run_in_threadpool(get_360p, videoid)
    return {"url": url}

@app.get("/api/stream/edu/{videoid}")
async def api_edu(videoid: str):
    r = requests.get(
        EDU_STREAM_API_BASE_URL + videoid,
        headers=ua(),
        timeout=MAX_API_WAIT
    )
    r.raise_for_status()
    return r.json()

# ===============================
# BBS
# ===============================
@app.get("/api/bbs/posts")
async def bbs_posts():
    r = requests.get(BBS_EXTERNAL_API_BASE_URL + "/posts", headers=ua())
    return r.json()

@app.post("/api/bbs/post")
async def bbs_post(request: Request):
    data = await request.json()
    r = requests.post(
        BBS_EXTERNAL_API_BASE_URL + "/post",
        json=data,
        headers={"X-Original-Client-IP": request.client.host}
    )
    return r.json()
