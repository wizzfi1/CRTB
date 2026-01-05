import MetaTrader5 as mt5
from datetime import datetime
from backtest.market_h4_m5_backtest import run_backtest


def summarize(trades):
    wins = [t for t in trades if t > 0]
    losses = [t for t in trades if t < 0]

    return {
        "trades": len(trades),
        "winrate": round(len(wins) / len(trades) * 100, 2) if trades else 0,
        "pnl": sum(trades),
        "avg_win": sum(wins) / len(wins) if wins else 0,
        "avg_loss": sum(losses) / len(losses) if losses else 0,
    }


if __name__ == "__main__":
    mt5.initialize()
    mt5.symbol_select("EURUSDm", True)

    trades = run_backtest(
        "EURUSDm",
        datetime(2025, 9, 1),
        datetime(2025, 12, 31),
    )

    print("\n=== H4 → M5 MARKET (STRENGTH + FIRST PULLBACK) ===")
    print(summarize(trades))
