import MetaTrader5 as mt5

def calculate_lot(symbol, risk_usd, entry, sl):
    info = mt5.symbol_info(symbol)
    if not info:
        return None

    tick_value = info.trade_tick_value
    tick_size = info.trade_tick_size

    risk_per_lot = abs(entry - sl) / tick_size * tick_value
    if risk_per_lot <= 0:
        return None

    lot = risk_usd / risk_per_lot
    lot = max(info.volume_min, min(lot, info.volume_max))
    lot = round(lot / info.volume_step) * info.volume_step

    return round(lot, 2)
