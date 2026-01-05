import MetaTrader5 as mt5
from datetime import datetime, timezone

from backtest.market_m5_backtest_runner import run_market_m5_backtest
from backtest.metrics import summarize
from backtest.data_loader import load_m1_history  # reuse loader

SYMBOL = "EURUSDm"

mt5.initialize()
mt5.symbol_select(SYMBOL, True)

start = datetime(2025, 9, 23, tzinfo=timezone.utc)
end   = datetime(2025, 12, 29, tzinfo=timezone.utc)

h4 = mt5.copy_rates_range(SYMBOL, mt5.TIMEFRAME_H4, start, end)
m5 = mt5.copy_rates_range(SYMBOL, mt5.TIMEFRAME_M5, start, end)

trades = run_market_m5_backtest(
    list(h4),
    list(m5),
    risk_usd=2500,
    rr=2.5
)

stats = summarize([
    {"result": t["result"]} for t in trades
])

print("\n=== H4 → M5 MARKET BACKTEST RESULTS ===")
print(stats)
