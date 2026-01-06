class CRTState:
    def __init__(self):
        self.active = False
        self.bias = None
        self.high = None
        self.low = None
        self.eq = None
        self.crt_time = None
        self.trades_taken = 0
        self.invalidated = False

        self.session = None
        self.session_announced = False  # ✅ NEW
