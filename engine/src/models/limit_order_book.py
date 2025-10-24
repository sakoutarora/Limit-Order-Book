from sortedcontainers import SortedDict
from src.models.price_level import PriceLevel
from src.models.order import Order
from src.utils.helper import to_cents


class LimitOrderBook:
    def __init__(self, ticker: str = None):
        self.ticker: str = ticker
        self.bids = SortedDict(lambda x: -x) 
        self.asks = SortedDict() 
        self.order_map = {}

    def get_side_struct(self, side):
        return self.bids if side == 1 else self.asks
    
    def to_serializable_dict(self):
        """Convert the entire LOB into a pure dict (JSON/pickle friendly)."""
        return {
            "ticker": self.ticker,
            "bids": [
                {"price": price, "level": level.to_serializable_dict()}
                for price, level in self.bids.items()
            ],
            "asks": [
                {"price": price, "level": level.to_serializable_dict()}
                for price, level in self.asks.items()
            ],
            "order_map": self.order_map
        }
    
    @classmethod
    def from_serializable_dict(cls, data, order_cls):
        """Rebuild LimitOrderBook from its serialized dict form."""
        lob = cls(data["ticker"])
        for side_name, sorted_prices in [("bids", data["bids"]), ("asks", data["asks"])]:
            side = lob.bids if side_name == "bids" else lob.asks
            for entry in sorted_prices:
                price = entry["price"]
                level_data = entry["level"]
                level = PriceLevel.from_serializable_dict(level_data, order_cls)
                side[price] = level
        lob.order_map = data.get("order_map", {})
        return lob

    def __repr__(self):
        return f"<LimitOrderBook ticker={self.ticker} bids={len(self.bids)} asks={len(self.asks)}>"