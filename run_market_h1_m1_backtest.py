import MetaTrader5 as mt5
from datetime import datetime

from backtest.market_h1_m1_backtest import run_backtest


def summarize(trades, risk=2500):
    if not trades:
        return {}

    equity = 0
    peak = 0
    max_dd = 0

    wins = []
    losses = []

    for t in trades:
        equity += t
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)

        if t > 0:
            wins.append(t)
        else:
            losses.append(t)

    return {
        "trades": len(trades),
        "winrate": round(len(wins) / len(trades) * 100, 2),
        "pnl": round(sum(trades), 2),
        "avg_win": round(sum(wins) / len(wins), 2) if wins else 0,
        "avg_loss": round(sum(losses) / len(losses), 2) if losses else 0,
        "max_drawdown": round(max_dd, 2),
        "max_drawdown_R": round(max_dd / risk, 2),
    }


if __name__ == "__main__":
    mt5.initialize()
    mt5.symbol_select("EURUSDm", True)

    trades = run_backtest(
        "EURUSDm",
        datetime(2024, 11, 25),
        datetime(2025, 1, 7),
    )

    print("\n=== H1 → M1 MARKET BACKTEST ===")
    print(summarize(trades))
