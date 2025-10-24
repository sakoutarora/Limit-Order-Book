def to_cents(price_float: float) -> int:
    """Convert float price to integer cents for precision."""
    return int(round(price_float * 100))

def find_ticker_from_order_id (order_id: str):
    return order_id.split("_")[0]