from .instances import try_instances

EDU_STREAM_API_BASE_URL = "https://siawaseok.duckdns.org/api/stream/"
EDU_VIDEO_API_BASE_URL = "https://siawaseok.duckdns.org/api/video2/"
STREAM_YTDL_API_BASE_URL = "https://yudlp.vercel.app/stream/"
SHORT_STREAM_API_BASE_URL = "https://yt-dl-kappa.vercel.app/short/"

def search_videos(q):
    return try_instances(
        "search",
        "/search",
        params={
            "q": q,
            "type": "video"
        }
    )

def get_comments(video_id):
    return try_instances(
        "comments",
        f"/api/v1/comments/{video_id}"
    )

def stream_sources(video_id):
    return [
        f"{EDU_STREAM_API_BASE_URL}{video_id}",
        f"{STREAM_YTDL_API_BASE_URL}{video_id}",
        f"{SHORT_STREAM_API_BASE_URL}{video_id}",
    ]
