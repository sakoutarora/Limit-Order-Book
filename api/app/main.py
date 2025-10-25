from fastapi import FastAPI
from app.api.routes import orders, websocket
from app.tasks.poller import start_poller
from app.core.grpc_client import grpc_client
from contextlib import asynccontextmanager
from app.core.redis import init_redis_connection
import redis.asyncio as redis
import asyncio
from app.tasks.trades import start_trade_subscriber

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP LOGIC ---
    print("Application startup: Starting poller...")
    app.state.redis = init_redis_connection()
    await start_poller()
    asyncio.create_task(start_trade_subscriber(app.state.redis))
    # Yield control to the application to handle requests
    try:
        yield

    finally:
        # --- SHUTDOWN LOGIC ---
        await app.state.redis.close()
        print("Application shutdown: Closing gRPC client...")
        await grpc_client.close()

app = FastAPI(title="Trading Gateway API", lifespan=lifespan)

# Routers
app.include_router(orders.router)
app.include_router(websocket.router)
