import MetaTrader5 as mt5
from datetime import datetime, timezone


def load_history(symbol, timeframe, start, end, chunk_size=5000):
    """
    Robust loader for TF >= M5 (H1, H4, etc).
    Uses copy_rates_from_pos to avoid MT5 range bugs.
    """
    all_rates = []
    pos = 0

    # Ensure UTC-aware
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    while True:
        chunk = mt5.copy_rates_from_pos(
            symbol,
            timeframe,
            pos,
            chunk_size
        )

        if chunk is None or len(chunk) == 0:
            break

        all_rates.extend(chunk)
        pos += chunk_size

        last_time = datetime.fromtimestamp(
            chunk[-1]["time"], tz=timezone.utc
        )

        # Stop once we've gone past requested start
        if last_time < start:
            break

    filtered = [
        r for r in all_rates
        if start <= datetime.fromtimestamp(
            r["time"], tz=timezone.utc
        ) <= end
    ]

    filtered.sort(key=lambda x: x["time"])

    if not filtered:
        raise RuntimeError(
            f"No data returned for TF={timeframe}"
        )

    return filtered


def load_m1_history(symbol, start, end, chunk_size=50000):
    """
    Robust M1 loader (unchanged).
    """
    all_rates = []
    pos = 0

    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    while True:
        chunk = mt5.copy_rates_from_pos(
            symbol,
            mt5.TIMEFRAME_M1,
            pos,
            chunk_size
        )

        if chunk is None or len(chunk) == 0:
            break

        all_rates.extend(chunk)
        pos += chunk_size

        last_time = datetime.fromtimestamp(
            chunk[-1]["time"], tz=timezone.utc
        )

        if last_time < start:
            break

    filtered = [
        r for r in all_rates
        if start <= datetime.fromtimestamp(
            r["time"], tz=timezone.utc
        ) <= end
    ]

    filtered.sort(key=lambda x: x["time"])
    return filtered
