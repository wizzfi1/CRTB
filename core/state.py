_last_h4_time = None

def first_pullback(h4_time):
    global _last_h4_time
    if _last_h4_time == h4_time:
        return False
    _last_h4_time = h4_time
    return True
