import time
import MetaTrader5 as mt5

from config.settings import SYMBOL, RR_TARGET, RISK_PER_TRADE_USD
from core.mt5_connector import connect
from core.sessions import session_allowed
from core.trend import h4_trend
from core.entry import pullback_entry
from core.execution import place_market
from risk.fixed_risk import calculate_lot
from notifications.telegram import send

connect(SYMBOL)

send(
    "🚀 *Wizfi TBot STARTED*\n"
    "Mode: H4 → M1 MARKET\n"
    "Risk: $2500\n"
    "RR: 2.5\n"
    "Sessions: London + NY\n"
    "Guards: Trend strength + First pullback\n"
)

last_h4_trade_time = None

while True:
    try:
        if mt5.positions_get() or mt5.orders_get():
            time.sleep(15)
            continue

        if not session_allowed():
            time.sleep(30)
            continue

        h4 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_H4, 1, 300)
        m1 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M1, 0, 50)

        if h4 is None or m1 is None:
            time.sleep(10)
            continue

        bias, ok = h4_trend(list(h4))
        if not ok:
            time.sleep(10)
            continue

        h4_time = h4[-1]["time"]
        if last_h4_trade_time == h4_time:
            time.sleep(10)
            continue

        window = list(m1[-20:])
        entry = pullback_entry(window, bias)
        if not entry:
            time.sleep(10)
            continue

        # 🔒 lock pullback immediately
        last_h4_trade_time = h4_time

        recent = window[-10:]
        if bias == "BUY":
            sl = min(c["low"] for c in recent)
            tp = entry + (entry - sl) * RR_TARGET
        else:
            sl = max(c["high"] for c in recent)
            tp = entry - (sl - entry) * RR_TARGET

        lot = calculate_lot(SYMBOL, RISK_PER_TRADE_USD, entry, sl)
        if not lot:
            time.sleep(10)
            continue

        send(
            f"📌 *MARKET ENTRY*\n"
            f"Symbol: {SYMBOL}\n"
            f"Bias: {bias}\n"
            f"Entry: {entry}\n"
            f"SL: {sl}\n"
            f"TP: {tp}\n"
            f"RR: {RR_TARGET}"
        )

        result, error = place_market(SYMBOL, bias, lot, sl, tp)
        if result:
            send(f"✅ *TRADE OPENED*\nTicket: {result.order}")
        else:
            send(f"❌ *ORDER FAILED*\n{error}")

        time.sleep(60)

    except Exception as e:
        send(f"⚠️ *BOT ERROR*\n{e}")
        time.sleep(30)
