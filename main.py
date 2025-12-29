import time
import MetaTrader5 as mt5

from mt5.connector import connect
from config.settings import *
from model.crt_controller import CRTController
from execution.liquidity import liquidity_sweep
from execution.displacement import displacement, bos
from execution.entry import find_fvg
from execution.executor import place_limit
from risk.fixed_risk import calculate_lot_size
from utils.telegram import TelegramNotifier

connect()

notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

crt = CRTController(
    SYMBOL,
    CRT_TIMEFRAME,
    MIN_DISPLACEMENT_PCT,
    MAX_TRADES_PER_CRT
)

while True:
    crt.update()

    if not crt.allow_trade():
        time.sleep(1)
        continue

    rates = mt5.copy_rates_from_pos(
        SYMBOL,
        ENTRY_TIMEFRAME,
        0,
        20
    )

    if not liquidity_sweep(rates, crt.state.bias, notifier):
        continue

    if not displacement(rates[-1], notifier):
        continue

    if not bos(rates, crt.state.bias):
        continue

    entry = find_fvg(rates, crt.state.bias, notifier)
    if not entry:
        continue

    if crt.state.bias == "BUY":
        sl = min(r["low"] for r in rates[-5:])
        tp = crt.state.high
    else:
        sl = max(r["high"] for r in rates[-5:])
        tp = crt.state.low

    lot = calculate_lot_size(
        SYMBOL,
        RISK_PER_TRADE_NAIRA,
        entry,
        sl
    )

    if not lot:
        continue

    place_limit(
        SYMBOL,
        crt.state.bias,
        lot,
        entry,
        sl,
        tp,
        notifier
    )

    crt.register_trade()
    time.sleep(60)
