from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.tasks.poller import register_client, unregister_client
from app.tasks.trades import unregister_client_trades, register_client_trades

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/book/{ticker}")
async def book_ws(ws: WebSocket, ticker: str):
    await ws.accept()
    register_client("book", ws, ticker)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        unregister_client("book", ws, ticker)


@router.websocket("/trades")
async def trades_ws(ws: WebSocket):
    await ws.accept()
    # fetch this from cache queue instead of polling ths way
    register_client_trades("trades", ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        unregister_client_trades("trades", ws)