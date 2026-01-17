import requests
import instances

# 外部ストリーム API
EDU_STREAM_API_BASE_URL = "https://siawaseok.duckdns.org/api/stream/"
EDU_VIDEO_API_BASE_URL  = "https://siawaseok.duckdns.org/api/video2/"
STREAM_YTDL_API_BASE_URL = "https://yudlp.vercel.app/stream/"
SHORT_STREAM_API_BASE_URL = "https://yt-dl-kappa.vercel.app/short/"

HEADERS = {"User-Agent": "iwashi-tube"}
TIMEOUT = 6


def search_videos(query: str):
    def task(instance):
        r = requests.get(
            f"{instance}/api/v1/search",
            params={"q": query, "type": "video"},
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    return instances.try_instances("search", task)


def get_comments(video_id: str):
    def task(instance):
        r = requests.get(
            f"{instance}/api/v1/comments/{video_id}",
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    return instances.try_instances("comments", task)


def stream_sources(video_id: str):
    # 優先順フォールバック
    for base in (
        EDU_STREAM_API_BASE_URL,
        EDU_VIDEO_API_BASE_URL,
        STREAM_YTDL_API_BASE_URL,
        SHORT_STREAM_API_BASE_URL,
    ):
        try:
            r = requests.get(base + video_id, timeout=TIMEOUT)
            if r.ok:
                return r.json()
        except:
            pass
    return None
