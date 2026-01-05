# backtest/market_backtest_runner.py

from datetime import datetime
from core.trend import h4_trend
from core.entry import pullback_entry


def run_market_backtest(h4_data, m1_data, risk_usd=2500, rr=2.5):
    trades = []
    active_trade = None

    for i in range(30, len(m1_data) - 1):
        candle = m1_data[i]

        # -----------------------------
        # MANAGE ACTIVE TRADE
        # -----------------------------
        if active_trade:
            hi, lo = candle["high"], candle["low"]

            if active_trade["bias"] == "BUY":
                if lo <= active_trade["sl"]:
                    active_trade["result"] = -risk_usd
                    trades.append(active_trade)
                    active_trade = None
                elif hi >= active_trade["tp"]:
                    active_trade["result"] = risk_usd * rr
                    trades.append(active_trade)
                    active_trade = None
            else:
                if hi >= active_trade["sl"]:
                    active_trade["result"] = -risk_usd
                    trades.append(active_trade)
                    active_trade = None
                elif lo <= active_trade["tp"]:
                    active_trade["result"] = risk_usd * rr
                    trades.append(active_trade)
                    active_trade = None

            continue

        # -----------------------------
        # TREND (H4)
        # -----------------------------
        h4_index = int(i / 240)
        bias = h4_trend(h4_data[: h4_index + 1])

        if not bias:
            continue

        # -----------------------------
        # ENTRY (M1 MARKET)
        # -----------------------------
        window = m1_data[i - 20 : i]
        entry = pullback_entry(window, bias)

        if not entry:
            continue

        # -----------------------------
        # SL / TP (RR = 2.5)
        # -----------------------------
        if bias == "BUY":
            sl = min(c["low"] for c in window[-5:])
            tp = entry + (entry - sl) * rr
        else:
            sl = max(c["high"] for c in window[-5:])
            tp = entry - (sl - entry) * rr

        # -----------------------------
        # OPEN MARKET TRADE
        # -----------------------------
        active_trade = {
            "bias": bias,
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "result": None
        }

    return trades
