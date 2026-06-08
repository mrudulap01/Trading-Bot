from enum import Enum, auto

class OrderSide(str, Enum):
    """Represents the side of a trading order."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """
    Represents supported order types.
    Note: Binance Futures Testnet maps STOP_LIMIT functionality to STOP.
    """
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LIMIT = "STOP_LIMIT"  # Internal application type
    STOP = "STOP"              # Binance API type


class OrderStatus(str, Enum):
    """Represents the lifecycle status of an order on Binance."""
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    EXPIRED_IN_MATCH = "EXPIRED_IN_MATCH"
