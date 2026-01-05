# backtest/backtest_runner.py

import MetaTrader5 as mt5
from datetime import datetime

from core.trend import h1_trend
from core.entry import pullback_entry
from risk.fixed_risk import calculate_lot_size
from config.settings import *


def normalize(rates):
    keys = [
        "time", "open", "high", "low",
        "close", "tick_volume", "spread", "real_volume"
    ]
    return [dict(zip(keys, r)) for r in rates]


def load_history(symbol, timeframe, start, end, chunk=20_000):
    data = []
    pos = 0

    while True:
        chunk_data = mt5.copy_rates_from_pos(symbol, timeframe, pos, chunk)
        if chunk_data is None or len(chunk_data) == 0:
            break

        data.extend(normalize(chunk_data))
        pos += chunk

        if datetime.fromtimestamp(chunk_data[-1][0]) < start:
            break

    filtered = [
        r for r in data
        if start <= datetime.fromtimestamp(r["time"]) <= end
    ]
    filtered.sort(key=lambda x: x["time"])
    return filtered


def session_allowed(ts):
    """
    London: 07:00–10:59 UTC
    New York: 13:00–16:59 UTC
    """
    hour = datetime.fromtimestamp(ts).hour

    london = 7 <= hour <= 10
    new_york = 13 <= hour <= 16

    return london or new_york


def run_backtest(symbol, start, end):

    h1 = load_history(symbol, TREND_TF, start, end)
    m5 = load_history(symbol, ENTRY_TF, start, end)

    if not h1 or not m5:
        raise RuntimeError("Missing H1 or M5 data")

    trades = []
    stats = {
        "trend_ok": 0,
        "session_ok": 0,
        "entries": 0,
        "lot_valid": 0,
        "trades": 0
    }

    h1_index = 0
    trend_bias = None
    trades_taken_this_h1 = 0
    last_h1_time = None

    for i in range(60, len(m5) - 1):
        candle = m5[i]
        t = candle["time"]

        # --- SESSION FILTER ---
        if not session_allowed(t):
            continue

        stats["session_ok"] += 1

        # --- Sync H1 index ---
        while h1_index + 1 < len(h1) and h1[h1_index + 1]["time"] <= t:
            h1_index += 1

        current_h1_time = h1[h1_index]["time"]

        # --- Reset per new H1 ---
        if last_h1_time != current_h1_time:
            trades_taken_this_h1 = 0
            last_h1_time = current_h1_time

        trend_bias = h1_trend(h1[:h1_index + 1])
        if not trend_bias:
            continue

        stats["trend_ok"] += 1

        if trades_taken_this_h1 >= MAX_TRADES_PER_TREND:
            continue

        window = m5[i - 60:i]
        entry = pullback_entry(window, trend_bias)
        if not entry:
            continue

        stats["entries"] += 1

        # --- SL / TP ---
        if trend_bias == "BUY":
            sl = min(c["low"] for c in window[-5:])
            tp = entry + (entry - sl) * RR_TARGET
        else:
            sl = max(c["high"] for c in window[-5:])
            tp = entry - (sl - entry) * RR_TARGET

        lot = calculate_lot_size(symbol, RISK_PER_TRADE_USD, entry, sl)
        if not lot:
            continue

        stats["lot_valid"] += 1

        # --- SIMULATE ---
        result = None
        for fwd in m5[i + 1:]:
            hi, lo = fwd["high"], fwd["low"]

            if trend_bias == "BUY":
                if lo <= sl:
                    result = -RISK_PER_TRADE_USD
                    break
                if hi >= tp:
                    result = RR_TARGET * RISK_PER_TRADE_USD
                    break
            else:
                if hi >= sl:
                    result = -RISK_PER_TRADE_USD
                    break
                if lo <= tp:
                    result = RR_TARGET * RISK_PER_TRADE_USD
                    break

        if result is not None:
            trades.append({"result": result})
            trades_taken_this_h1 += 1
            stats["trades"] += 1

    print("\n--- DIAGNOSTIC COUNTS ---")
    for k, v in stats.items():
        print(f"{k}: {v}")

    return trades
