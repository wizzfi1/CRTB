import MetaTrader5 as mt5
from datetime import datetime

print("Initializing MT5:", mt5.initialize())

symbol = "EURUSDm"
print("Symbol select:", mt5.symbol_select(symbol, True))

rates = mt5.copy_rates_range(
    symbol,
    mt5.TIMEFRAME_M1,
    datetime(2025, 9, 23),
    datetime(2025, 9, 24)
)

print("Rates object:", rates)
print("Rates length:", None if rates is None else len(rates))
