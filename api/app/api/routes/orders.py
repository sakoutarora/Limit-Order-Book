from fastapi import APIRouter, HTTPException, status
from app.model.schema import PlaceOrderIn, PlaceOrderOut, ModifyOrderIn, CancelOrderOut, OrderView
from app.core.grpc_client import grpc_client

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=PlaceOrderOut)
async def place_order(data: PlaceOrderIn):
    try:
        resp = await grpc_client.submit_order(data.price, data.quantity, str(data.side), data.ticker)
        order_id = getattr(resp, "order_id", None)
        return PlaceOrderOut(order_id=order_id)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{order_id}", response_model=CancelOrderOut)
async def modify_order(order_id: str, data: ModifyOrderIn):
    if data.order_id != order_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Mismatched order_id")
    resp = await grpc_client.modify_order(order_id, data.updated_price)
    return CancelOrderOut(success=getattr(resp, "success", True))


@router.delete("/{order_id}", response_model=CancelOrderOut)
async def cancel_order(order_id: str):
    resp = await grpc_client.cancel_order(order_id)
    return CancelOrderOut(success=getattr(resp, "success", True))