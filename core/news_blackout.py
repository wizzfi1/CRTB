import json
import os
from datetime import datetime, timezone

NEWS_FILE = "data/news_blackouts.json"
CACHE_TTL_SECONDS = 60  # reload every 60s

_last_load_time = 0
_cached_blackouts = []


def _load_blackouts():
    global _last_load_time, _cached_blackouts

    try:
        if not os.path.exists(NEWS_FILE):
            _cached_blackouts = []
            return

        with open(NEWS_FILE, "r") as f:
            raw = json.load(f)

        parsed = []
        for item in raw:
            start = datetime.strptime(
                item["start"], "%Y-%m-%d %H:%M"
            ).replace(tzinfo=timezone.utc)

            end = datetime.strptime(
                item["end"], "%Y-%m-%d %H:%M"
            ).replace(tzinfo=timezone.utc)

            parsed.append({
                "start": start,
                "end": end,
                "reason": item.get("reason", "High-impact news")
            })

        _cached_blackouts = parsed
        _last_load_time = datetime.now().timestamp()

    except Exception:
        # Fail-closed: if file is broken, block trading
        _cached_blackouts = [{
            "start": datetime.min.replace(tzinfo=timezone.utc),
            "end": datetime.max.replace(tzinfo=timezone.utc),
            "reason": "NEWS FILE ERROR"
        }]


def in_news_blackout(now_utc=None):
    """
    Auto-reloading blackout checker.
    Returns:
        (True, reason) or (False, None)
    """
    global _last_load_time

    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    # Reload periodically
    if datetime.now().timestamp() - _last_load_time > CACHE_TTL_SECONDS:
        _load_blackouts()

    for blk in _cached_blackouts:
        if blk["start"] <= now_utc <= blk["end"]:
            return True, blk["reason"]

    return False, None
