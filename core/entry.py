from core.trend import ema

def pullback_entry(window, bias):
    closes = [c["close"] for c in window]
    ema20 = ema(closes, 20)[-1]

    prev = window[-2]
    curr = window[-1]

    if bias == "BUY":
        if prev["close"] < ema20 and curr["close"] > ema20:
            return curr["close"]

    if bias == "SELL":
        if prev["close"] > ema20 and curr["close"] < ema20:
            return curr["close"]

    return None
