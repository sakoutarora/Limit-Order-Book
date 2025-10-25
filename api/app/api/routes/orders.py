from fastapi import APIRouter, HTTPException, status, Depends
from app.model.schema import PlaceOrderIn, PlaceOrderOut, ModifyOrderIn, CancelOrderOut, OrderView
from app.core.grpc_client import grpc_client
from app.core.redis import get_redis 
import traceback
from app.proto import lob_pb2
from typing import List
from google.protobuf.json_format import MessageToDict
import json

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=PlaceOrderOut)
async def place_order(data: PlaceOrderIn, redis_client=Depends(get_redis)):
    try:
        resp = await grpc_client.submit_order(data.price, data.quantity, str(data.side), data.ticker)
        order_id = getattr(resp, "order_id", None)

        trades: List[lob_pb2.Trade] = getattr(resp, "trades", [])
        for trade in trades:
            trade_dict = MessageToDict(trade, preserving_proto_field_name=True)
            trade_json = json.dumps(trade_dict)
            await redis_client.publish("trades", trade_json)

        return PlaceOrderOut(order_id=order_id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{order_id}", response_model=CancelOrderOut)
async def modify_order(order_id: str, data: ModifyOrderIn, redis_client=Depends(get_redis)):
    resp = await grpc_client.modify_order(order_id, data.updated_price, data.updated_quantity)
    
    trades :List[lob_pb2.Trade]  = getattr(resp, "trades", [])
    for trade in trades:
        trade_dict = MessageToDict(trade, preserving_proto_field_name=True)
        trade_json = json.dumps(trade_dict)
        redis_client.publish("trades", trade_json)

    return CancelOrderOut(success=getattr(resp, "success", True))


@router.delete("/{order_id}", response_model=CancelOrderOut)
async def cancel_order(order_id: str):
    resp = await grpc_client.cancel_order(order_id)
    return CancelOrderOut(success=getattr(resp, "success", True))