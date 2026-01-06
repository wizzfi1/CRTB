import MetaTrader5 as mt5
from datetime import datetime, timezone


def load_history(symbol, timeframe, start, end, chunk_size=5000):
    """
    Generic MT5 history loader for TF >= M5 (H4, H1, M15, etc).
    Uses copy_rates_range safely.
    """
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    rates = mt5.copy_rates_range(symbol, timeframe, start, end)

    if rates is None or len(rates) == 0:
        raise RuntimeError(f"No data returned for timeframe {timeframe}")

    return list(rates)


def load_m1_history(symbol, start, end, chunk_size=50000):
    """
    Force-load M1 history using positional chunks.
    All timestamps are handled as UTC-aware datetimes.
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
            chunk[-1]["time"],
            tz=timezone.utc
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
