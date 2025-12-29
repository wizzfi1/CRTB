def find_fvg(rates, bias, notifier=None):
    if len(rates) < 5:
        return None

    if bias == "BUY":
        if rates[-2]["low"] > rates[-4]["high"]:
            entry = (rates[-2]["low"] + rates[-4]["high"]) / 2
            if notifier:
                notifier.send(f"🎯 *Bullish FVG*\nEntry: {entry}")
            return entry

    if bias == "SELL":
        if rates[-2]["high"] < rates[-4]["low"]:
            entry = (rates[-2]["high"] + rates[-4]["low"]) / 2
            if notifier:
                notifier.send(f"🎯 *Bearish FVG*\nEntry: {entry}")
            return entry

    return None
