import grpc
from concurrent import futures
from src.controller.order_grpc_controller import OrderGrpcController
from src.proto import lob_pb2_grpc

import asyncio
import grpc
from src.controller.order_grpc_controller import OrderGrpcController
from src.proto import lob_pb2_grpc
from src.persistance.wal import WAL
from src.persistance.snapshot import SnapshotManager


async def serve():
    # Create an asynchronous gRPC server
    server = grpc.aio.server()
    wal = WAL("./wal.log")
    snapshot_manager = SnapshotManager("./snapshots")
    controller = await OrderGrpcController.create(wal, snapshot_manager)

    # Register your service implementation
    lob_pb2_grpc.add_OrderServiceServicer_to_server(controller, server)

    # Bind to port
    server.add_insecure_port('[::]:50051')
    print("🚀 Async gRPC Order Service running on port 50051")

    # Start the server
    await server.start()

    # Keep running until explicitly stopped (Ctrl+C or cancellation)
    await server.wait_for_termination()
