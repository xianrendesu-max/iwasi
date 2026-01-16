import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .api import search_videos, get_comments, stream_sources

BASE_DIR = os.path.dirname(__file__)

app = FastAPI()

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/search", response_class=HTMLResponse)
def search(request: Request, q: str):
    videos = search_videos(q) or []
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "videos": videos,
            "q": q
        }
    )

@app.get("/watch/{video_id}", response_class=HTMLResponse)
def watch(request: Request, video_id: str):
    return templates.TemplateResponse(
        "watch.html",
        {
            "request": request,
            "video_id": video_id,
            "streams": stream_sources(video_id)
        }
    )

@app.get("/api/comments/{video_id}")
def comments(video_id: str):
    return JSONResponse(
        get_comments(video_id) or {}
    )
