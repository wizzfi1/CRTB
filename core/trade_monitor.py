# core/trade_monitor.py

import MetaTrader5 as mt5
from datetime import datetime, timedelta
from notifications.telegram import send
from config.settings import MAGIC_NUMBER


class TradeMonitor:
    def __init__(self):
        self.open_positions = set()

    def update(self):
        """
        Detect closed trades by comparing open positions.
        """
        current_positions = mt5.positions_get()
        current_tickets = set()

        if current_positions:
            for p in current_positions:
                if p.magic == MAGIC_NUMBER:
                    current_tickets.add(p.ticket)

        # --- detect closed positions ---
        closed_tickets = self.open_positions - current_tickets

        for ticket in closed_tickets:
            self._handle_closed_trade(ticket)

        # update snapshot
        self.open_positions = current_tickets

    def _handle_closed_trade(self, ticket):
        """
        Fetch closed trade info and alert Telegram
        """
        from_time = datetime.utcnow() - timedelta(days=1)
        to_time = datetime.utcnow()

        deals = mt5.history_deals_get(from_time, to_time)
        if not deals:
            return

        pnl = None
        symbol = None

        for d in deals:
            if d.position_id == ticket and d.magic == MAGIC_NUMBER:
                pnl = round(d.profit, 2)
                symbol = d.symbol

        if pnl is None:
            return

        result = "WIN ✅" if pnl > 0 else "LOSS ❌"

        send(
            f"📤 *TRADE CLOSED*\n"
            f"Symbol: {symbol}\n"
            f"Ticket: {ticket}\n"
            f"Result: {result}\n"
            f"PnL: {pnl}"
        )
