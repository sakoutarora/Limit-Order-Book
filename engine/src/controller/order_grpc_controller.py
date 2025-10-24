import grpc
from concurrent import futures
from src.proto import lob_pb2_grpc, lob_pb2
from src.service.matching_engine import OrderEngine
from src.persistance.wal import WAL
from src.persistance.snapshot import SnapshotManager
import asyncio
from src.db.lob_db import LobDb
from datetime import datetime
import traceback
from src.models.order import Order
class OrderGrpcController(lob_pb2_grpc.OrderServiceServicer):
    def __init__(self, wal: WAL, snaphost_manager: SnapshotManager):
        self._db = LobDb()
        self.wal = wal
        self.service = OrderEngine(wal, self._db)
        
        self.snaphost_manager = snaphost_manager
        self._op_count_since_snapshot = 0
        self._snapshot_every_ops = 10
        self._lock = asyncio.Lock()

    @classmethod
    async def create(cls, wal: WAL, snapshot_manager: SnapshotManager):
        self = cls(wal, snapshot_manager)
        await self.recover()
        return self

    async def recover(self):
        print("Recpvering .. ")
        snap_seq, state = await self.snaphost_manager.load_latest()
        if state is not None:
            await self._db.set_all_state(state) 

        async for rec in self.wal.read_from(0):
            op = rec["op"]
            data = rec["data"]
            await self._apply_operation_no_wal(op, data)
        print("Recovery complete")

    async def _maybe_snapshot(self):
        if self._op_count_since_snapshot >= self._snapshot_every_ops:
            async with self._lock:
                state = await self._db.get_serializable_state()
                last_seq = self.wal._last_seq
                await self.snaphost_manager.write_snapshot(state)
                await self.wal.truncate()
                self._op_count_since_snapshot = 0
        self._op_count_since_snapshot += 1

    async def _apply_operation_no_wal(self, op, data):
        """
        Apply operation to in-memory structures without writing a WAL entry.
        """

        if op == "submit":
            await self.service.submit_order(**data, skip_wal=True)
        elif op == "modify":
            await self.service.modify_oder(**data, skip_wal=True)
        elif op == "cancel":
            await self.service.cancel_order(**data, skip_wal=True)
        else:
            pass
    
    async def SubmitOrder(self, request, context):
        try:
            await self._maybe_snapshot()
            order, trades = await self.service.submit_order(
                ticker=request.tikcer,
                side=int(request.type),
                price=request.price,
                qty=request.quantity
            )
            
            response_trades = []
            for trade in trades:
                response_trades.append(lob_pb2.Trade(
                    unique_id=str(trade.unique_id),
                    timestamp=int(datetime.now().timestamp() * 1000),
                    price=trade.price,
                    qty=int(trade.qty),
                    bid_order_id=trade.bid_order_id,
                    ask_order_id=trade.ask_order_id
                ))

            return lob_pb2.OrderResponse(
                status="ok",
                order_id=str(order.id),
                trades=response_trades
            )
        
        except Exception as e:
            traceback.print_exc()
            raise e
    
    async def ModifyOrder(self, request, context):
        try:
            await self._maybe_snapshot()
            order, trades = self.service.modify_oder(
                order_id=request.order_id,
                new_price=request.new_price,
                new_quantity=request.new_quantity
            )
            
            response_trades = []
            for trade in trades:
                response_trades.append(lob_pb2.Trade(
                    unique_id=str(trade.unique_id),
                    timestamp=int(datetime.now().timestamp() * 1000),
                    price=trade.price,
                    qty=int(trade.qty),
                    bid_order_id=trade.bid_order_id,
                    ask_order_id=trade.ask_order_id
                ))

            return lob_pb2.OrderResponse(
                status="ok",
                order_id=str(order.id),
                trades=response_trades
            )
        
        except Exception as e:
            traceback.print_exc()
            raise e

    async def CancelOrder(self, request, context):

        try:
            await self._maybe_snapshot()
            order: Order = await self.service.cancel_order(
                order_id=request.order_id
            )
            if order is None:
                return lob_pb2.OrderResponse(
                    status="error",
                    message="Order not found"
                )
            
            return lob_pb2.OrderResponse(
                status="ok",
                order_id=str(order.id)
            )
            
        except Exception as e:
            traceback.print_exc()
            raise e

    async def GetLob(self, request, context):
        lob = await self.service.get_lob(request.ticker)
        asks_level = []
        bids_level = []
        if lob:
            for key, val in lob.asks.items():
                asks_level.append(lob_pb2.PriceLevel(
                    price=key/100.0,
                    total_qty=val.total_qty
                ))

            for key, val in lob.bids.items():
                bids_level.append(lob_pb2.PriceLevel(
                    price=key/100.0,
                    total_qty=val.total_qty
                ))

        response = lob_pb2.LobResponse(
            ticker=request.ticker,
            asks=asks_level,
            bids=bids_level
        )

        return response