from src.models.limit_order_book import LimitOrderBook
import asyncio
from src.models.order import Order
class LobDb:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LobDb, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.lobs = {}
            self._lock = asyncio.Lock()
            self._initialized = True

    async def add_lob(self, ticker: str):
        async with self._lock:
            if ticker not in self.lobs:
                self.lobs[ticker] = LimitOrderBook(ticker)
            return self.lobs[ticker]
    
    async def set_lob(self, ticker: str, lob: LimitOrderBook):
        async with self._lock:
            self.lobs[ticker] = lob

    async def get_lob(self, ticker: str):
        async with self._lock:
            return self.lobs.get(ticker)
        
    async def get_serializable_state(self):
        async with self._lock:
            return {
                ticker: lob.to_serializable_dict()
                for ticker, lob in self.lobs.items()
            }

    async def set_all_state(self, state):
        async with self._lock:
            self.lobs = {
                ticker: LimitOrderBook.from_serializable_dict(data, Order)
                for ticker, data in state.items()
            }