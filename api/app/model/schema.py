from pydantic import BaseModel, Field, validator, conint, confloat
from typing import List, Optional


class PlaceOrderIn(BaseModel):
    quantity: conint(gt=0)
    price: confloat(gt=0)
    side: int
    ticker: str

    @validator("side")
    def side_valid(cls, v):
        if v not in (1, -1):
            raise ValueError("side must be 1 (buy) or -1 (sell)")
        return v

    @validator("price")
    def price_multiple(cls, v):
        if abs(round(v * 100) / 100 - v) > 1e-9:
            raise ValueError("price must be multiple of 0.01")
        return v


class PlaceOrderOut(BaseModel):
    order_id: str


class ModifyOrderIn(BaseModel):
    order_id: str
    updated_price: confloat(gt=0)


class CancelOrderOut(BaseModel):
    success: bool


class OrderView(BaseModel):
    order_id: str
    order_price: float
    order_quantity: int
    traded_quantity: int
    order_alive: bool
    average_traded_price: Optional[float] = None


class TradeView(BaseModel):
    trade_id: str
    execution_timestamp: float
    price: float
    qty: int
    bid_order_id: str
    ask_order_id: str


class LobSnapshot(BaseModel):
    ts: float
    bids: List[dict]
    asks: List[dict]