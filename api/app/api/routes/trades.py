from fastapi import APIRouter, HTTPException, status, Depends

router = APIRouter(prefix="/trades", tags=["Trades"])

@router.get("/")
async def get_trades():
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)