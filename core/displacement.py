def is_displacement(candle, bias, min_body_ratio=0.6):
    high = candle["high"]
    low = candle["low"]
    open_ = candle["open"]
    close = candle["close"]

    rng = high - low
    if rng <= 0:
        return False

    body = abs(close - open_)
    if body / rng < min_body_ratio:
        return False

    if bias == "BUY" and close <= open_:
        return False

    if bias == "SELL" and close >= open_:
        return False

    return True
