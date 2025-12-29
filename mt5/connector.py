import MetaTrader5 as mt5


def connect():
    if not mt5.initialize():
        raise RuntimeError("❌ MT5 initialization failed")


def shutdown():
    mt5.shutdown()


def candles(symbol, timeframe, bars, shift=0):
    return mt5.copy_rates_from_pos(symbol, timeframe, shift, bars)


def tick(symbol):
    return mt5.symbol_info_tick(symbol)
