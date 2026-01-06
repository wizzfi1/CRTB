def pullback_entry(candles, bias):
    """
    Structural M1 pullback entry.
    Returns entry price or None.
    """
    if len(candles) < 20:
        return None

    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    closes = [c["close"] for c in candles]

    # -------------------------
    # IDENTIFY IMPULSE LEG
    # -------------------------
    if bias == "BUY":
        impulse_high = max(highs[:-5])
        pullback_low = min(lows[-5:])

        # Must pull back but NOT break structure
        if pullback_low < min(lows[:-10]):
            return None

        # Rejection candle
        last = candles[-1]
        if last["close"] > last["open"] and last["low"] == pullback_low:
            return last["close"]

    else:
        impulse_low = min(lows[:-5])
        pullback_high = max(highs[-5:])

        if pullback_high > max(highs[:-10]):
            return None

        last = candles[-1]
        if last["close"] < last["open"] and last["high"] == pullback_high:
            return last["close"]

    return None
