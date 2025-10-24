class Price:
    """Value object representing a price in cents."""

    def __init__(self, value_cents: int):
        if value_cents < 0:
            raise ValueError("Price cannot be negative.")
        self._value = value_cents

    @property
    def value(self) -> int:
        return self._value

    def __eq__(self, other):
        return isinstance(other, Price) and self._value == other._value

    def __lt__(self, other):
        return isinstance(other, Price) and self._value < other._value

    def __repr__(self):
        return f"Price({self._value / 100:.2f})"