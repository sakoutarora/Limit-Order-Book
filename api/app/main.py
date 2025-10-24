from fastapi import FastAPI
from app.api.routes import orders, websocket
from app.tasks.poller import start_poller
from app.core.grpc_client import grpc_client
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP LOGIC ---
    print("Application startup: Starting poller...")
    await start_poller()

    # Yield control to the application to handle requests
    yield

    # --- SHUTDOWN LOGIC ---
    print("Application shutdown: Closing gRPC client...")
    await grpc_client.close()

app = FastAPI(title="Trading Gateway API", lifespan=lifespan)

# Routers
app.include_router(orders.router)
app.include_router(websocket.router)
