import MetaTrader5 as mt5
from config.settings import MAGIC_NUMBER


def place_limit(symbol, bias, lot, entry, sl, tp, notifier=None):
    order_type = (
        mt5.ORDER_TYPE_BUY_LIMIT
        if bias == "BUY"
        else mt5.ORDER_TYPE_SELL_LIMIT
    )

    result = mt5.order_send({
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": entry,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": MAGIC_NUMBER,
        "comment": "CRT_BOT"
    })

    if notifier:
        notifier.send(
            f"📌 *Limit Order Placed*\n"
            f"Direction: {bias}\n"
            f"Entry: {entry}\n"
            f"SL: {sl}\n"
            f"TP: {tp}\n"
            f"Lot: {lot}\n"
            f"Risk: ₦3000\n"
            f"Reason: CRT + Session + Liquidity + Displacement + FVG"
        )

    return result
