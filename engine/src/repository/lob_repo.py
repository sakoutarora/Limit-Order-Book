from src.models.order import Order
from src.models.limit_order_book import LimitOrderBook
from src.models.price_level import PriceLevel
import traceback
from src.models.trade import Trade
from typing import Tuple, List
from src.utils.helper import to_cents

class LimitOrderBookRepository:

    def add_order(self, lob: LimitOrderBook, incoming: Order) -> Tuple[LimitOrderBook, List[Trade]]:
        try:
            opposite = lob.asks if incoming.side == 1 else lob.bids
            trades = []

            while incoming.remaining_qty > 0 and len(opposite) > 0:
                best_price = next(iter(opposite))

                if (incoming.side == 1 and best_price > incoming.price) or \
                (incoming.side == -1 and best_price < incoming.price):
                    break

                level: PriceLevel = opposite[best_price]
                resting: Order = level.get_first_order()
                if not resting:
                    break

                trade_qty = min(incoming.remaining_qty, resting.remaining_qty)
                trade_price = resting.price

                # Apply trade
                incoming.record_trade(trade_price, trade_qty)
                resting.record_trade(trade_price, trade_qty)
                level.total_qty -= trade_qty

                trades.append(Trade(
                    ticker=lob.ticker,
                    unique_id=f"{incoming.id}-{resting.id}",
                    price=trade_price,
                    qty=trade_qty,
                    bid_order_id=incoming.id if incoming.side == 1 else resting.id,
                    ask_order_id=resting.id if incoming.side == 1 else incoming.id,
                ))

                # Remove filled orders/levels
                if resting.remaining_qty == 0:
                    level.orders.popitem(last=False)
                    del lob.order_map[resting.id]

                if level.total_qty == 0:
                    del opposite[best_price]

            # Remaining qty => place it in own side
            if incoming.remaining_qty > 0:
                side_struct = lob.get_side_struct(incoming.side)
                level = side_struct.get(incoming.price)
                if not level:
                    level = PriceLevel(incoming.price)
                    side_struct[incoming.price] = level
                level.add_order(incoming)
                lob.order_map[incoming.id] = incoming

            return lob, trades
        
        except Exception as e:
            traceback.print_exc()
            raise e
        
    def cancel_oder(self, lob: LimitOrderBook, order_id: str) -> Order:
        if order_id not in lob.order_map:
            return None
        
        order = lob.order_map[order_id]
        side_struct = lob.get_side_struct(order.side)

        level: PriceLevel = side_struct[order.price]
        order = level.cancel_order(order_id)

        if level.total_qty == 0:
            del side_struct[order.price]
        del lob.order_map[order_id]
        return order


    def modify_oder(self, lob: LimitOrderBook, order_id: str, new_price: float, new_qty: int) -> Tuple[LimitOrderBook, List[Trade], Order]:
        order = self.cancel_oder(lob, order_id)

        order.price = to_cents(new_price)
        order.remaining_qty = new_qty
        order.original_qty = new_qty
        new_lob, trades = self.add_order(lob, order)
        
        return new_lob, trades, order
