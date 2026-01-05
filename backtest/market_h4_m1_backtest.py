import MetaTrader5 as mt5
from datetime import datetime

from core.trend import ema, atr
from backtest.data_loader import load_history

RISK = 2500
RR = 2.5


def run_backtest(symbol, start, end):
    if not mt5.initialize():
        raise RuntimeError("MT5 not initialized")

    h4 = load_history(symbol, mt5.TIMEFRAME_H4, start, end)
    m1 = load_history(symbol, mt5.TIMEFRAME_M1, start, end)

    trades = []
    traded_h4 = set()

    for i in range(30, len(m1) - 1):
        candle = m1[i]

        # Find current H4 candle
        h4_idx = None
        for j in range(len(h4) - 1):
            if h4[j]["time"] <= candle["time"] < h4[j + 1]["time"]:
                h4_idx = j
                break

        if h4_idx is None or h4_idx < 60:
            continue

        h4_closed = h4[:h4_idx]
        h4_time = h4[h4_idx]["time"]

        if h4_time in traded_h4:
            continue

        closes_h4 = [c["close"] for c in h4_closed]
        ema20 = ema(closes_h4, 20)[-1]
        ema50 = ema(closes_h4, 50)[-1]

        if ema20 > ema50:
            bias = "BUY"
        elif ema20 < ema50:
            bias = "SELL"
        else:
            continue

        h4_atr = atr(h4_closed, 14)
        if not h4_atr:
            continue

        if abs(ema20 - ema50) < 0.25 * h4_atr:
            continue

        # M1 timing
        m1_window = m1[i - 20:i]
        closes_m1 = [c["close"] for c in m1_window]
        ema20_m1 = ema(closes_m1, 20)[-1]

        prev = m1[i - 1]
        curr = m1[i]

        if bias == "BUY":
            if not (prev["close"] < ema20_m1 and curr["close"] > ema20_m1):
                continue
        else:
            if not (prev["close"] > ema20_m1 and curr["close"] < ema20_m1):
                continue

        entry = curr["close"]

        recent = m1[i - 10:i]
        if bias == "BUY":
            sl = min(c["low"] for c in recent)
            tp = entry + (entry - sl) * RR
        else:
            sl = max(c["high"] for c in recent)
            tp = entry - (sl - entry) * RR

        result = None
        for fwd in m1[i + 1:]:
            hi, lo = fwd["high"], fwd["low"]

            if bias == "BUY":
                if lo <= sl:
                    result = -RISK
                    break
                if hi >= tp:
                    result = RISK * RR
                    break
            else:
                if hi >= sl:
                    result = -RISK
                    break
                if lo <= tp:
                    result = RISK * RR
                    break

        if result is not None:
            trades.append(result)
            traded_h4.add(h4_time)

    return trades
