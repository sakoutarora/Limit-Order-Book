from collections import OrderedDict


class PriceLevel:
    """Aggregate representing a price level with queued orders (FIFO)."""
    def __init__(self, price_c: int):
        self.price = price_c
        self.orders = OrderedDict()
        self.total_qty = 0

    def add_order(self, order):
        """Add order to this price level."""
        self.orders[order.id] = order
        self.total_qty += order.remaining_qty

    def remove_filled_order(self):
        """Remove the oldest order if filled completely."""
        if not self.orders:
            return
        first_id, first_order = next(iter(self.orders.items()))
        if first_order.remaining_qty == 0:
            del self.orders[first_id]

    def cancel_order(self, order_id):
        """Cancel order by ID in O(1)."""
        if order_id in self.orders:
            order = self.orders.pop(order_id)
            self.total_qty -= order.remaining_qty
            return order
        return None
    
    def get_first_order(self):
        if not self.orders:
            return None
        return next(iter(self.orders.values()))
    
    def to_serializable_dict(self):
        """Convert PriceLevel into pure-dict form for snapshotting."""
        return {
            "price": self.price,
            "total_qty": self.total_qty,
            "orders": [
                {
                    "id": o.id,
                    "side": o.side,
                    "price": o.price,
                    "original_qty": o.original_qty,
                    "remaining_qty": o.remaining_qty
                }
                for o in self.orders.values()
            ]
        }
    
    @classmethod
    def from_serializable_dict(cls, data, order_cls):
        """Rebuild PriceLevel (and orders) from serialized data."""
        level = cls(data["price"])
        for order_data in data["orders"]:
            order = order_cls(
                order_id=order_data["id"],
                side=order_data["side"],
                price_c=order_data["price"],
                quantity=order_data["original_qty"],
                remaining_qty=order_data["remaining_qty"]
            )
            level.add_order(order)
        level.total_qty = data["total_qty"]
        return level

    def __repr__(self):
        return f"<PriceLevel price={self.price/100:.2f} total_qty={self.total_qty}>"