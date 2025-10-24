from src.db.lob_db import LobDb
from src.repository.lob_repo import LimitOrderBookRepository
from src.utils.helper import to_cents
from src.models.order import Order
import asyncio
from src.persistance.wal import WAL
class OrderEngine:
    """Application service handling LOB operations."""

    def __init__(self, wal: WAL, db: LobDb):
        self.wal = wal
        self._lock = asyncio.Lock()
        self._db  = db
        self._lob = LimitOrderBookRepository()

    
    async def submit_order(self, ticker: str, side: int, price: float, qty: int, skip_wal=False) -> bool:
        if not skip_wal:
            await self.wal.append("submit", {"ticker": ticker, "side": side, "price": price, "qty": qty})

        price_c = to_cents(price)
        order = Order(side, price_c, qty)
        lob = await self._db.add_lob(ticker)
        if lob:
            lob = self._lob.add_order(lob, order)
            await self._db.set_lob(ticker, lob)
            return True
        return False
    
    async def modify_oder(self, order_id: str, new_price: float, new_qty: int, skip_wal=False):
        if not skip_wal:
            await self.wal.append("modify", {"order_id": order_id, "new_price": new_price, "new_qty": new_qty})

        return self.lob.modify_order(order_id, new_price, new_qty)
    

    async def cancel_order(self, order_id: str, skip_wal=False):
        if not skip_wal:
            await self.wal.append("cancel", {"order_id": order_id})
        self._lob.cancel_oder(order_id)

    async def get_lob(self, ticker: str):
        lob = await self._db.get_lob(ticker)
        if lob:
            return lob
        return None