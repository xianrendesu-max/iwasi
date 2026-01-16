import requests

from iwashi_tube.instances import try_instances

# =========================
# 外部ストリームAPI
# =========================

EDU_STREAM_API_BASE_URL = "https://siawaseok.duckdns.org/api/stream/"
EDU_VIDEO_API_BASE_URL  = "https://siawaseok.duckdns.org/api/video2/"
STREAM_YTDL_API_BASE_URL = "https://yudlp.vercel.app/stream/"
SHORT_STREAM_API_BASE_URL = "https://yt-dl-kappa.vercel.app/short/"

HEADERS = {"User-Agent": "iwashi-tube"}
TIMEOUT = 6


# =========================
# 検索
# =========================

def search_videos(query: str):
    def task(instance):
        url = f"{instance}/api/v1/search"
        r = requests.get(
            url,
            params={"q": query, "type": "video"},
            headers=HEADERS,
            timeout=TIMEOUT
        )
        r.raise_for_status()
        return r.json()

    return try_instances("search", task)


# =========================
# コメント
# =========================

def get_comments(video_id: str):
    def task(instance):
        url = f"{instance}/api/v1/comments/{video_id}"
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()

    return try_instances("comments", task)


# =========================
# ストリーム多段フォールバック
# =========================

def stream_sources(video_id: str):
    """
    優先順:
    1. EDU stream
    2. EDU video2
    3. ytdlp
    4. short
    """

    # ① EDU stream
    try:
        r = requests.get(
            f"{EDU_STREAM_API_BASE_URL}{video_id}",
            timeout=TIMEOUT
        )
        if r.ok:
            return r.json()
    except:
        pass

    # ② EDU video2
    try:
        r = requests.get(
            f"{EDU_VIDEO_API_BASE_URL}{video_id}",
            timeout=TIMEOUT
        )
        if r.ok:
            return r.json()
    except:
        pass

    # ③ ytdlp
    try:
        r = requests.get(
            f"{STREAM_YTDL_API_BASE_URL}{video_id}",
            timeout=TIMEOUT
        )
        if r.ok:
            return r.json()
    except:
        pass

    # ④ short
    try:
        r = requests.get(
            f"{SHORT_STREAM_API_BASE_URL}{video_id}",
            timeout=TIMEOUT
        )
        if r.ok:
            return r.json()
    except:
        pass

    return None
