import MetaTrader5 as mt5
from config.settings import MAGIC_NUMBER

FILLING_MODES = [
    mt5.ORDER_FILLING_IOC,
    mt5.ORDER_FILLING_FOK,
    mt5.ORDER_FILLING_RETURN,
]

def place_market(symbol, bias, lot, sl, tp):
    info = mt5.symbol_info(symbol)
    tick = mt5.symbol_info_tick(symbol)

    if not info or not tick:
        return None, "NO_SYMBOL_OR_TICK"

    if bias == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
        sl_dist = price - sl
    else:
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
        sl_dist = sl - price

    min_stop = info.trade_stops_level * info.point
    if min_stop > 0 and sl_dist < min_stop:
        return None, f"SL_TOO_CLOSE (min {min_stop:.5f})"

    last_error = None

    for filling in FILLING_MODES:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 50,
            "magic": MAGIC_NUMBER,
            "comment": "H4-M1 MARKET",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling,
        }

        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            return result, None

        last_error = result.comment if result else "NO_RESPONSE"

    return None, last_error
