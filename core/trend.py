import numpy as np
import MetaTrader5 as mt5

EMA_FAST = 20
EMA_SLOW = 50
EMA_REGIME = 200
MIN_EMA_SEPARATION = 0.0003  # EURUSD tuned

MIN_EMA_SEPARATION_H1 = 0.0001
MIN_EMA_SEPARATION_H4 = 0.0003

def ema(values, period):
    alpha = 2 / (period + 1)
    ema_vals = [values[0]]
    for v in values[1:]:
        ema_vals.append(alpha * v + (1 - alpha) * ema_vals[-1])
    return ema_vals


def h4_trend(candles):
    """
    Returns:
        bias: "BUY" | "SELL" | None
        ok: bool (trend strength confirmed)
    """
    if len(candles) < EMA_REGIME + 5:
        return None, False

    closes = [c["close"] for c in candles]

    ema20 = ema(closes, EMA_FAST)
    ema50 = ema(closes, EMA_SLOW)
    ema200 = ema(closes, EMA_REGIME)

    # Use last CLOSED candle
    i = -2

    price = closes[i]

    # -------------------------
    # REGIME FILTER (HARD)
    # -------------------------
    if price > ema200[i]:
        regime = "BUY"
    elif price < ema200[i]:
        regime = "SELL"
    else:
        return None, False

    # -------------------------
    # MOMENTUM ALIGNMENT
    # -------------------------
    if regime == "BUY":
        if not (ema20[i] > ema50[i] > ema200[i]):
            return None, False
        separation = ema20[i] - ema50[i]
    else:
        if not (ema20[i] < ema50[i] < ema200[i]):
            return None, False
        separation = ema50[i] - ema20[i]

    if separation < MIN_EMA_SEPARATION:
        return None, False

    # -------------------------
    # SLOPE CONFIRMATION
    # -------------------------
    slope = ema50[i] - ema50[i - 3]

    if regime == "BUY" and slope <= 0:
        return None, False
    if regime == "SELL" and slope >= 0:
        return None, False

    return regime, True


