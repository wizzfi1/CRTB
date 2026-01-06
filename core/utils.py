def ema(values, period):
    """
    Proper EMA calculation
    values: list of floats
    period: int
    """
    if len(values) < period:
        return None

    k = 2 / (period + 1)
    ema_value = sum(values[:period]) / period  # SMA seed

    for price in values[period:]:
        ema_value = price * k + ema_value * (1 - k)

    return ema_value
