import asyncio
import grpc
from app.proto import lob_pb2, lob_pb2_grpc
from app.core import settings


class GRPCClient:
    def __init__(self):
        self._channel = None
        self._stub = None
        self._lock = asyncio.Lock()

    async def ensure_stub(self):
        """Ensure gRPC stub is created (singleton pattern)."""
        if self._stub is None:
            async with self._lock:
                if self._stub is None:
                    self._channel = grpc.aio.insecure_channel(settings.settings.GRPC_TARGET)
                    self._stub = lob_pb2_grpc.OrderServiceStub(self._channel)
        return self._stub

    async def submit_order(self, price: float, qty: int, side: str, ticker: str = "DEFAULT"):
        """Submit a new order."""
        stub = await self.ensure_stub()
        request = lob_pb2.OrderRequest(
            tikcer=ticker,
            type=side,     # expected to be "1" or "-1"
            price=price,
            quantity=qty,
        )
        return await stub.SubmitOrder(request)

    async def modify_order(self, order_id: int, new_price: float, new_qty: int):
        """Modify an existing order."""
        stub = await self.ensure_stub()
        request = lob_pb2.ModifyOrderRequest(
            order_id=order_id,
            new_price=new_price,
            new_quantity=new_qty,
        )
        return await stub.ModifyOrder(request)

    async def cancel_order(self, order_id: str):
        """Cancel an order by ID."""
        stub = await self.ensure_stub()
        request = lob_pb2.CancelOrderRequest(order_id=order_id)
        return await stub.CancelOrder(request)

    async def get_lob(self, ticker: str = "DEFAULT"):
        """Fetch the current Limit Order Book (LOB) for a given ticker."""
        stub = await self.ensure_stub()
        request = lob_pb2.LobRequest(ticker=ticker)
        return await stub.GetLob(request)
    
    async def get_order(self, order_id: str):
        """Fetch an order by ID."""
        stub = await self.ensure_stub()
        request = lob_pb2.CancelOrderRequest(order_id=order_id)
        return await stub.GetOder(request)

    async def close(self):
        """Close the gRPC channel."""
        if self._channel:
            await self._channel.close()


grpc_client = GRPCClient()