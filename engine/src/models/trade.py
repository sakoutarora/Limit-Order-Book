

class Trade:
    def __init__(self, ticker: str, unique_id: str, price: float, qty: int, bid_order_id: str, ask_order_id: str):
        self.unique_id = unique_id
        self.price = price
        self.qty = qty
        self.bid_order_id = bid_order_id
        self.ask_order_id = ask_order_id
        self.ticker = ticker
