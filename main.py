import json, random, requests, urllib.parse
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# ========= API =========
EDU_STREAM_API_BASE_URL = "https://siawaseok.duckdns.org/api/stream/"
EDU_VIDEO_API_BASE_URL  = "https://siawaseok.duckdns.org/api/video2/"
STREAM_YTDL_API_BASE_URL = "https://yudlp.vercel.app/stream/"
SHORT_STREAM_API_BASE_URL = "https://yt-dl-kappa.vercel.app/short/"

invidious_api_data = {
    "search": ["https://api-five-zeta-55.vercel.app/"],
    "video": [
        "https://invidious.lunivers.trade/",
        "https://invidious.ducks.party/",
        "https://iv.melmac.space/",
        "https://iv.duti.dev/"
    ],
    "comments": [
        "https://invidious.lunivers.trade/",
        "https://invidious.ducks.party/",
        "https://iv.melmac.space/"
    ]
}

def api_get(base_list, path):
    for base in random.sample(base_list, len(base_list)):
        try:
            r = requests.get(base + "api/v1" + path, timeout=8)
            if r.status_code == 200:
                return r.json()
        except:
            pass
    return None

# ========= APP =========
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ========= SEARCH =========
@app.get("/", response_class=HTMLResponse)
def search(request: Request, q: str = ""):
    results = []
    if q:
        results = api_get(invidious_api_data["search"],
            f"/search?q={urllib.parse.quote(q)}&hl=jp") or []
    return templates.TemplateResponse(
        "search.html", {"request": request, "results": results, "q": q}
    )

# ========= WATCH =========
@app.get("/watch", response_class=HTMLResponse)
def watch(request: Request, v: str, mode: str = "stream"):
    video = api_get(invidious_api_data["video"], f"/videos/{v}")
    comments = api_get(invidious_api_data["comments"], f"/comments/{v}")
    edu = requests.get(EDU_STREAM_API_BASE_URL + v).json()
    ytdlp = requests.get(STREAM_YTDL_API_BASE_URL + v).json()

    stream_url = ""
    if ytdlp and ytdlp.get("formats"):
        for f in ytdlp["formats"]:
            if f.get("itag") == "18":
                stream_url = f["url"]
                break

    return templates.TemplateResponse("watch.html", {
        "request": request,
        "video": video,
        "comments": comments.get("comments", []) if comments else [],
        "mode": mode,
        "stream_url": stream_url,
        "edu_url": edu.get("url") if edu else "",
        "video_id": v
    })

# ========= FAVORITES =========
@app.get("/favorites", response_class=HTMLResponse)
def favorites(request: Request):
    return templates.TemplateResponse("favorites.html", {"request": request})
