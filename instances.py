import requests
import random
import time

from iwashi_tube.instances import try_instances

# =========================
# 共通設定
# =========================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iwashi-tube)"
}

TIMEOUT = 5


# =========================
# 検索
# =========================

def search_videos(query: str):
    """
    Invidious 検索API
    """
    def task(instance):
        url = f"{instance}/api/v1/search"
        params = {
            "q": query,
            "type": "video",
            "sort_by": "relevance"
        }
        r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()

    return try_instances(task)


# =========================
# コメント取得
# =========================

def get_comments(video_id: str):
    """
    Invidious コメントAPI
    """
    def task(instance):
        url = f"{instance}/api/v1/comments/{video_id}"
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()

    return try_instances(task)


# =========================
# ストリーム取得
# =========================

def stream_sources(video_id: str):
    """
    再生ソース取得（adaptiveFormats 含む）
    """
    def task(instance):
        url = f"{instance}/api/v1/videos/{video_id}"
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()

        streams = []

        # 通常フォーマット
        for f in data.get("formatStreams", []):
            streams.append({
                "url": f.get("url"),
                "quality": f.get("qualityLabel"),
                "mime": f.get("mimeType")
            })

        # adaptive（音声/映像分離）
        for f in data.get("adaptiveFormats", []):
            streams.append({
                "url": f.get("url"),
                "quality": f.get("qualityLabel", "adaptive"),
                "mime": f.get("mimeType")
            })

        return streams

    return try_instances(task)
