import asyncio
import time
from typing import Dict, Set, Any
from fastapi.responses import JSONResponse
from app.core.grpc_client import grpc_client
from app.core.settings import settings
import traceback

BOOK_WS: Set[Any] = set()
_started = False


def register_client(kind: str, ws, ticker):
    BOOK_WS.add((ws, ticker))


def unregister_client(kind: str, ws):
    BOOK_WS.discard(ws)


async def start_poller():
    global _started
    if _started:
        return
    _started = True
    asyncio.create_task(_poll())


async def _poll():
    while True:
        try:
            for ws, ticker in list(BOOK_WS):
                try:
                    lob = await grpc_client.get_lob(ticker)
                    ts = time.time()

                    bids = [{"price": float(l.price), "qty": int(l.total_qty)} for l in lob.bids[:5]]
                    asks = [{"price": float(l.price), "qty": int(l.total_qty)} for l in lob.asks[:5]]
                    snapshot = JSONResponse(content={"ts": ts, "bids": bids, "asks": asks}).body.decode()
                    await _broadcast(snapshot, ws)
                except Exception as e:
                    traceback.print_exc()
                    BOOK_WS.discard(ws)
            
            await asyncio.sleep(settings.SNAPSHOT_INTERVAL_SEC)
        except Exception as e:
            traceback.print_exc()
            await asyncio.sleep(2)


async def _broadcast(msg: str, ws: Any):
    await ws.send_text(msg)
