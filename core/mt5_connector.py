import MetaTrader5 as mt5
import sys

def connect(symbol):
    if not mt5.initialize():
        print("MT5 initialize failed")
        sys.exit(1)

    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol {symbol}")
        sys.exit(1)

    info = mt5.account_info()
    print(f"Connected to MT5 | Account: {info.login}")
