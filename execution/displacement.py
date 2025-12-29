def displacement(candle, notifier=None):
    body = abs(candle["close"] - candle["open"])
    rng = candle["high"] - candle["low"]

    valid = rng > 0 and body / rng >= 0.7

    if valid and notifier:
        notifier.send(
            f"⚡ *Displacement Confirmed*\n"
            f"Open: {candle['open']} Close: {candle['close']}"
        )

    return valid


def bos(rates, bias):
    last = rates[-1]

    if bias == "BUY":
        return last["close"] > max(r["high"] for r in rates[:-1])
    else:
        return last["close"] < min(r["low"] for r in rates[:-1])
