from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from iwashi_tube.api import (
    search_videos,
    get_comments,
    stream_sources,
)

app = FastAPI(title="イワシtube", version="1.0")

app.mount("/static", StaticFiles(directory="iwashi_tube/static"), name="static")
templates = Jinja2Templates(directory="iwashi_tube/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/watch/{video_id}", response_class=HTMLResponse)
async def watch(video_id: str, request: Request):
    return templates.TemplateResponse(
        "watch.html",
        {"request": request, "video_id": video_id},
    )


@app.get("/api/search")
async def api_search(q: str):
    result = search_videos(q)
    if result is None:
        raise HTTPException(status_code=503, detail="search failed")
    return result


@app.get("/api/comments/{video_id}")
async def api_comments(video_id: str):
    result = get_comments(video_id)
    if result is None:
        raise HTTPException(status_code=503, detail="comments failed")
    return result


@app.get("/api/streams/{video_id}")
async def api_streams(video_id: str):
    result = stream_sources(video_id)
    if result is None:
        raise HTTPException(status_code=503, detail="streams failed")
    return result


@app.get("/health")
async def health():
    return {"status": "ok"}
