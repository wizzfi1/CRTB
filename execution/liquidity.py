def liquidity_sweep(rates, bias, notifier=None):
    last = rates[-1]
    highs = [r["high"] for r in rates[:-1]]
    lows = [r["low"] for r in rates[:-1]]

    if bias == "BUY":
        swept = last["low"] < min(lows) and last["close"] > min(lows)
    else:
        swept = last["high"] > max(highs) and last["close"] < max(highs)

    if swept and notifier:
        notifier.send(
            f"💧 *Liquidity Sweep*\nBias: {bias}\nPrice: {last['close']}"
        )

    return swept
