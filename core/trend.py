import numpy as np

def ema(values, period):
    values = np.array(values, dtype=float)
    k = 2 / (period + 1)
    ema_vals = [values[0]]
    for v in values[1:]:
        ema_vals.append(v * k + ema_vals[-1] * (1 - k))
    return ema_vals


def atr(candles, period=14):
    trs = []
    for i in range(1, len(candles)):
        h = candles[i]["high"]
        l = candles[i]["low"]
        pc = candles[i-1]["close"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return sum(trs[-period:]) / period if len(trs) >= period else None


def h4_trend(h4):
    closes = [c["close"] for c in h4]

    ema_fast = ema(closes, 20)[-1]
    ema_slow = ema(closes, 50)[-1]
    atr14 = atr(h4, 14)

    if atr14 is None:
        return None, False

    # 🔒 TREND STRENGTH GUARD
    if abs(ema_fast - ema_slow) < 0.25 * atr14:
        return None, False

    if ema_fast > ema_slow:
        return "BUY", True
    if ema_fast < ema_slow:
        return "SELL", True

    return None, False
