
from typing import Dict, Set, Any
import asyncio
import traceback
import redis.asyncio as redis

REDIS_CHANNEL = "trades"
TRADE_WS: Set[Any] = set()

async def start_trade_subscriber(redis_client: redis.Redis):
    """
    Background task that subscribes to Redis 'trades' channel
    and pushes incoming messages to all connected WebSocket clients.
    """
    try:
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(REDIS_CHANNEL)
        print(f"Subscribed to Redis channel: {REDIS_CHANNEL}")

        async for message in pubsub.listen():
            if message is None:
                continue

            # Redis message format: {'type': 'message', 'pattern': None, 'channel': b'trades', 'data': b'{"..."}'}
            if message["type"] == "message":
                trade_data = message["data"]
                if isinstance(trade_data, bytes):
                    trade_data = trade_data.decode()

                # Push to all connected trade WebSockets
                await broadcast_trade(trade_data)

    except Exception:
        traceback.print_exc()
        await asyncio.sleep(2)
        asyncio.create_task(start_trade_subscriber(redis_client))  # restart on crash

async def broadcast_trade(trade_json: str):
    """
    Broadcast trade update to all WebSocket clients connected to TRADE_WS.
    """
    disconnected = set()
    for ws in list(TRADE_WS):
        try:
            await ws.send_text(trade_json)
        except Exception:
            disconnected.add(ws)

    # Remove dead clients
    for d in disconnected:
        TRADE_WS.discard(d)

def register_client_trades(kind: str, ws):
    TRADE_WS.add(ws)


def unregister_client_trades(kind: str, ws):
    TRADE_WS.discard(ws)
