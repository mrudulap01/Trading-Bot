from dataclasses import dataclass
from typing import Dict, Any, Optional
from bot.constants import OrderSide, OrderType, OrderStatus

@dataclass
class OrderResponse:
    """
    Strongly typed data model representing a Binance Futures order.
    Transforms raw JSON dictionaries into structured objects.
    """
    order_id: int
    symbol: str
    side: OrderSide
    type: OrderType
    status: OrderStatus
    quantity: float
    price: Optional[float] = None
    executed_qty: float = 0.0

    @classmethod
    def from_binance_response(cls, data: Dict[str, Any]) -> "OrderResponse":
        """
        Factory method to parse raw Binance API JSON into an OrderResponse.
        
        Args:
            data (Dict[str, Any]): The raw dictionary from Binance.
            
        Returns:
            OrderResponse: The parsed strongly-typed object.
        """
        # Safely parse numeric fields that might be strings in JSON
        price_val = data.get("price") or data.get("avgPrice")
        price = float(price_val) if price_val else None
        
        qty_val = data.get("origQty") or data.get("quantity")
        qty = float(qty_val) if qty_val else 0.0
        
        executed_qty_val = data.get("executedQty")
        executed_qty = float(executed_qty_val) if executed_qty_val else 0.0

        return cls(
            order_id=int(data.get("orderId", 0)),
            symbol=data.get("symbol", ""),
            side=OrderSide(data.get("side")),
            type=OrderType(data.get("type")),
            status=OrderStatus(data.get("status", "NEW")),
            quantity=qty,
            price=price,
            executed_qty=executed_qty
        )
