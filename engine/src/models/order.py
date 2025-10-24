import time
import uuid


class Order:
    """Entity representing a single order in the LOB."""

    def __init__(self, side: int, price_c: int, quantity: int, remaining_qty=None, order_id=None, ticker=None):
        self.id = order_id or str(ticker) + "_" + uuid.uuid4().hex[:12]
        self.side = side  # 1 = buy, -1 = sell
        self.price = price_c
        self.original_qty = quantity
        self.remaining_qty = remaining_qty or quantity
        self.traded_qty = 0
        self.trade_value_acc = 0  
        self.timestamp = time.time()
        self.alive = True
        self.ticker = ticker

    def record_trade(self, price_c: int, qty: int) -> None:
        """Record a trade execution."""
        self.traded_qty += qty
        self.remaining_qty -= qty
        self.trade_value_acc += price_c * qty
        if self.remaining_qty == 0:
            self.alive = False

    @property
    def avg_traded_price(self):
        """Average traded price in float."""
        if self.traded_qty == 0:
            return None
        return (self.trade_value_acc / self.traded_qty) / 100

    def __repr__(self):
        return (f"<Order id={self.id} side={'BUY' if self.side==1 else 'SELL'} "
                f"price={self.price/100:.2f} remaining={self.remaining_qty}>")
