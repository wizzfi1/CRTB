# execution/context.py

def h1_displacement(h1_block, min_body_pct=0.6):
    h_open = h1_block[0]["open"]
    h_close = h1_block[-1]["close"]
    h_high = max(c["high"] for c in h1_block)
    h_low = min(c["low"] for c in h1_block)

    rng = h_high - h_low
    body = abs(h_close - h_open)

    if rng == 0 or body / rng < min_body_pct:
        return None

    if h_close > (h_high + h_low) / 2:
        return "BUY"
    else:
        return "SELL"
