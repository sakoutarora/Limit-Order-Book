import asyncio
import time
from typing import Dict, Set, Any
from fastapi.responses import JSONResponse
from app.core.grpc_client import grpc_client
from app.core.settings import settings

BOOK_WS: Set[Any] = set()
TRADE_WS: Set[Any] = set()
_started = False


def register_client(kind: str, ws):
    (BOOK_WS if kind == "book" else TRADE_WS).add(ws)


def unregister_client(kind: str, ws):
    (BOOK_WS if kind == "book" else TRADE_WS).discard(ws)


async def start_poller():
    global _started
    if _started:
        return
    _started = True
    asyncio.create_task(_poll())


async def _poll():
    while True:
        try:
            lob = await grpc_client.get_lob()
            ts = time.time()

            bids = [{"price": float(l.price), "qty": int(l.qty)} for l in lob.bids[:5]]
            asks = [{"price": float(l.price), "qty": int(l.qty)} for l in lob.asks[:5]]
            snapshot = JSONResponse(content={"ts": ts, "bids": bids, "asks": asks}).body.decode()

            # Broadcast snapshot
            await _broadcast(snapshot, BOOK_WS)
            await asyncio.sleep(settings.SNAPSHOT_INTERVAL_SEC)
        except Exception as e:
            print("Poller error:", e)
            await asyncio.sleep(2)


async def _broadcast(msg: str, clients: Set[Any]):
    dead = []
    for ws in list(clients):
        try:
            await ws.send_text(msg)
        except Exception:
            dead.append(ws)
    for d in dead:
        clients.discard(d)