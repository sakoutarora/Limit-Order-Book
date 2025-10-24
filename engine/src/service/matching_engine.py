from src.db.lob_db import LobDb
from src.repository.lob_repo import LimitOrderBookRepository
from src.utils.helper import to_cents, find_ticker_from_order_id
from src.models.order import Order
import asyncio
from src.persistance.wal import WAL
from src.models.trade import Trade
from src.models.limit_order_book import LimitOrderBook
from typing import List, Tuple

class OrderEngine:
    """Application service handling LOB operations."""

    def __init__(self, wal: WAL, db: LobDb):
        self.wal = wal
        self._lock = asyncio.Lock()
        self._db  = db
        self._lob = LimitOrderBookRepository()

    
    async def submit_order(self, ticker: str, side: int, price: float, qty: int, skip_wal=False) -> Tuple[Order, List[Trade]]:
        if not skip_wal:
            await self.wal.append("submit", {"ticker": ticker, "side": side, "price": price, "qty": qty})
        price_c = to_cents(price)
        order = Order(side, price_c, qty, ticker=ticker)
        lob = await self._db.add_lob(ticker)
        if lob:
            lob, trades = self._lob.add_order(lob, order)
            await self._db.set_lob(ticker, lob)
            return order, trades
        return order,[]
    
    async def modify_oder(self, order_id: str, new_price: float, new_qty: int, skip_wal=False) -> Tuple[Order, List[Trade]]:
        if not skip_wal:
            await self.wal.append("modify", {"order_id": order_id, "new_price": new_price, "new_qty": new_qty})

        ticker = find_ticker_from_order_id(order_id)
        lob = await self._db.get_lob(ticker)
        if lob:
            new_lob, trades, order = await self._lob.modify_oder(lob, order_id, new_price, new_qty)
            await self._db.set_lob(ticker, new_lob)
            return order, trades
        return None, None
    

    async def cancel_order(self, order_id: str, skip_wal=False) -> Order:
        if not skip_wal:
            await self.wal.append("cancel", {"order_id": order_id})

        ticker = find_ticker_from_order_id(order_id)
        lob = await self._db.get_lob(ticker)
        if lob:
            return self._lob.cancel_oder(lob, order_id)
        return None

    async def get_lob(self, ticker: str) -> LimitOrderBook:
        lob = await self._db.get_lob(ticker)
        if lob:
            return lob
        return None