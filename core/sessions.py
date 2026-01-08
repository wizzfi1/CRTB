from datetime import datetime, timezone

LONDON_START = 7
LONDON_END = 16
NY_START = 12
NY_END = 21

def session_allowed():
    h = datetime.now(timezone.utc).hour
    return (LONDON_START <= h < LONDON_END) or (NY_START <= h < NY_END)


