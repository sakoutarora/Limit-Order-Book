def to_cents(price_float: float) -> int:
    """Convert float price to integer cents for precision."""
    return int(round(price_float * 100))