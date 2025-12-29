from datetime import datetime, time, timezone

LONDON_START = time(7, 0)
LONDON_END = time(10, 0)

NY_START = time(12, 0)
NY_END = time(15, 0)


def current_utc_time():
    return datetime.now(timezone.utc).time()


def in_london_session():
    now = current_utc_time()
    return LONDON_START <= now <= LONDON_END


def in_ny_session():
    now = current_utc_time()
    return NY_START <= now <= NY_END


def in_trading_session():
    return in_london_session() or in_ny_session()


def active_session_name():
    if in_london_session():
        return "London"
    if in_ny_session():
        return "New York"
    return None
