def summarize(trades):
    wins = [t for t in trades if t["result"] > 0]
    losses = [t for t in trades if t["result"] < 0]

    return {
        "trades": len(trades),
        "winrate": round(len(wins)/len(trades)*100, 2) if trades else 0,
        "pnl": sum(t["result"] for t in trades),
        "avg_win": sum(t["result"] for t in wins)/len(wins) if wins else 0,
        "avg_loss": sum(t["result"] for t in losses)/len(losses) if losses else 0,
    }
