import MetaTrader5 as mt5
from datetime import datetime, timezone

from backtest.data_loader import load_m1_history, load_history
from core.trend import h4_trend   # reused logic, timeframe-agnostic
from core.entry import pullback_entry


RR_TARGET = 2.5
RISK_PER_TRADE = 2500


def run_backtest(symbol, start, end):
    # ------------------------------
    # Load historical data
    # ------------------------------
    h1 = load_history(symbol, mt5.TIMEFRAME_H1, start, end)
    m1 = load_m1_history(symbol, start, end)

    if not h1 or not m1:
        raise RuntimeError("No data returned")

    trades = []

    last_h1_trade_time = None
    m1_index = 0

    # ------------------------------
    # Walk H1 candles
    # ------------------------------
    for i in range(200, len(h1) - 1):
        h1_slice = h1[: i + 1]

        bias, trend_ok = h4_trend(h1_slice)
        if not bias or not trend_ok:
            continue

        h1_time = h1[i]["time"]

        # 🔒 First pullback only (per H1 candle)
        if last_h1_trade_time == h1_time:
            continue

        # ------------------------------
        # Advance M1 index to H1 candle
        # ------------------------------
        while m1_index < len(m1) and m1[m1_index]["time"] < h1_time:
            m1_index += 1

        # ------------------------------
        # Scan M1 inside this H1 candle
        # ------------------------------
        for j in range(m1_index, min(m1_index + 60, len(m1))):
            window = m1[j - 20 : j]
            if len(window) < 20:
                continue

            entry = pullback_entry(window, bias)
            if not entry:
                continue

            # 🔒 Lock pullback immediately
            last_h1_trade_time = h1_time

            # ------------------------------
            # Structural SL / TP
            # ------------------------------
            recent = window[-10:]

            if bias == "BUY":
                sl = min(c["low"] for c in recent)
                risk = entry - sl
                tp = entry + risk * RR_TARGET
            else:
                sl = max(c["high"] for c in recent)
                risk = sl - entry
                tp = entry - risk * RR_TARGET

            if risk <= 0:
                break

            # ------------------------------
            # Simulate forward outcome
            # ------------------------------
            result = None

            for fwd in m1[j + 1 :]:
                if bias == "BUY":
                    if fwd["low"] <= sl:
                        result = -RISK_PER_TRADE
                        break
                    if fwd["high"] >= tp:
                        result = RR_TARGET * RISK_PER_TRADE
                        break
                else:
                    if fwd["high"] >= sl:
                        result = -RISK_PER_TRADE
                        break
                    if fwd["low"] <= tp:
                        result = RR_TARGET * RISK_PER_TRADE
                        break

            if result is not None:
                trades.append(result)

            break  # only first pullback

    return trades
