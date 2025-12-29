import MetaTrader5 as mt5
from model.state import CRTState
from utils.session import in_trading_session, active_session_name
from utils.telegram import TelegramNotifier
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


class CRTController:
    def __init__(self, symbol, timeframe, min_disp, max_trades):
        self.symbol = symbol
        self.tf = timeframe
        self.min_disp = min_disp
        self.max_trades = max_trades
        self.state = CRTState()

        self.notifier = TelegramNotifier(
            TELEGRAM_BOT_TOKEN,
            TELEGRAM_CHAT_ID
        )

    def update(self):
        rates = mt5.copy_rates_from_pos(self.symbol, self.tf, 1, 1)
        if rates is None or len(rates) == 0:
            return

        candle = rates[0]

        if self.state.crt_time != candle["time"]:
            self._reset()
            self._initialize(candle)

        # Session change alerts
        session = active_session_name()
        if session != self.state.session:
            self.state.session = session
            if session:
                self.notifier.send(
                    f"🕒 *{session} Session Open*\nEntries ENABLED"
                )
            else:
                self.notifier.send(
                    "⏹ *Sessions Closed*\nEntries DISABLED"
                )

    def _initialize(self, candle):
        rng = candle["high"] - candle["low"]
        body = abs(candle["close"] - candle["open"])

        if rng == 0 or body / rng < self.min_disp:
            return

        self.state.high = candle["high"]
        self.state.low = candle["low"]
        self.state.eq = (self.state.high + self.state.low) / 2
        self.state.crt_time = candle["time"]

        price = self._price()
        if price > self.state.eq:
            self.state.bias = "BUY"
            self.state.active = True
        elif price < self.state.eq:
            self.state.bias = "SELL"
            self.state.active = True

        if self.state.active:
            self.notifier.send(
                f"🧠 *CRT Initialized*\n"
                f"Bias: {self.state.bias}\n"
                f"High: {self.state.high}\n"
                f"Low: {self.state.low}\n"
                f"EQ: {round(self.state.eq, 5)}"
            )

    def allow_trade(self):
        if not self.state.active:
            return False
        if self.state.invalidated:
            return False
        if self.state.trades_taken >= self.max_trades:
            return False
        if not in_trading_session():
            return False

        price = self._price()
        return self.state.low <= price <= self.state.high

    def register_trade(self):
        self.state.trades_taken += 1

    def _reset(self):
        self.state = CRTState()

    def _price(self):
        t = mt5.symbol_info_tick(self.symbol)
        return (t.bid + t.ask) / 2 if t else None
