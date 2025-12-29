import MetaTrader5 as mt5


def calculate_lot_size(symbol, risk_amount, entry, stop_loss):
    info = mt5.symbol_info(symbol)
    if info is None:
        return None

    tick_value = info.trade_tick_value
    tick_size = info.trade_tick_size

    sl_distance = abs(entry - stop_loss)
    if sl_distance == 0:
        return None

    ticks = sl_distance / tick_size
    loss_per_lot = ticks * tick_value

    lot = risk_amount / loss_per_lot

    lot = max(info.volume_min, lot)
    lot = min(info.volume_max, lot)
    return round(lot, 2)
