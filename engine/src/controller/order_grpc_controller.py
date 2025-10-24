import grpc
from concurrent import futures
from src.proto import lob_pb2_grpc, lob_pb2
from src.service.matching_engine import OrderEngine
from src.persistance.wal import WAL
from src.persistance.snapshot import SnapshotManager
import asyncio
from src.db.lob_db import LobDb


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
            await self.service.modify_order(**data, skip_wal=True)
        elif op == "cancel":
            await self.service.cancel_order(**data, skip_wal=True)
        else:
            pass
    

    async def SubmitOrder(self, request_iterator, context):
        async for order_req in request_iterator:            
            result = await self.service.submit_order(
                ticker=order_req.tikcer,
                side=int(order_req.type),
                price=order_req.price,
                qty=order_req.quantity
            )
            await self._maybe_snapshot()

        return lob_pb2.OrderResponse(
            status="ok",
            message="All streamed orders processed successfully",
            order_id=0
        )

    async def ModifyOrder(self, request_iterator, context):
        for mod_req in request_iterator:
            result = self.service.modify_order(
                mod_req.order_id,
                mod_req.new_price,
                mod_req.new_quantity
            )
            await self._maybe_snapshot()
        return lob_pb2.OrderResponse(
            status="ok",
            message="All modifications applied",
            order_id=0
        )

    async def CancelOrder(self, request_iterator, context):
        for cancel_req in request_iterator:
            result = self.service.cancel_order(cancel_req.order_id)
            await self._maybe_snapshot()

        return lob_pb2.OrderResponse(
            status="ok",
            message="All cancellations processed",
            order_id=0
        )
    
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