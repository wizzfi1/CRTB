# test_trade.py
import MetaTrader5 as mt5
from datetime import datetime
from config.settings import SYMBOL
from notifications.telegram import send
from core.mt5_connector import connect

# ----------------------------
# CONNECT
# ----------------------------
connect(SYMBOL)
send("🧪 TEST TRADE SCRIPT STARTED")

symbol_info = mt5.symbol_info(SYMBOL)
tick = mt5.symbol_info_tick(SYMBOL)

if not symbol_info or not tick:
    send("❌ Symbol info unavailable")
    quit()

# ----------------------------
# VERY SMALL TEST TRADE
# ----------------------------
lot = 0.01  # 🔴 SAFE SIZE
price = tick.ask

sl = price - 0.0010   # ~10 pips
tp = price + 0.0010   # ~10 pips

request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": SYMBOL,
    "volume": lot,
    "type": mt5.ORDER_TYPE_BUY,
    "price": price,
    "sl": sl,
    "tp": tp,
    "deviation": 10,
    "magic": 999999,
    "comment": "EXECUTION TEST",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_FOK
}

result = mt5.order_send(request)

# ----------------------------
# RESULT CHECK
# ----------------------------
if result.retcode == mt5.TRADE_RETCODE_DONE:
    send(
        f"✅ TEST TRADE PLACED\n"
        f"Symbol: {SYMBOL}\n"
        f"Lot: {lot}\n"
        f"Price: {price}\n"
        f"SL: {sl}\n"
        f"TP: {tp}\n"
        f"Ticket: {result.order}"
    )
else:
    send(
        f"❌ TEST TRADE FAILED\n"
        f"Retcode: {result.retcode}\n"
        f"Comment: {result.comment}"
    )

mt5.shutdown()
