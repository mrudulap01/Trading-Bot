from typing import Optional, Union
from bot.constants import OrderSide, OrderType


class ValidationError(Exception):
    """Base exception class for all validation errors."""
    pass


class SymbolValidationError(ValidationError):
    """Raised when the trading symbol fails validation."""
    pass


class SideValidationError(ValidationError):
    """Raised when the order side fails validation."""
    pass


class OrderTypeValidationError(ValidationError):
    """Raised when the order type fails validation."""
    pass


class QuantityValidationError(ValidationError):
    """Raised when the order quantity fails validation."""
    pass


class PriceValidationError(ValidationError):
    """Raised when the order price fails validation."""
    pass


class StopPriceValidationError(ValidationError):
    """Raised when the stop price fails validation."""
    pass


def validate_symbol(symbol: str) -> None:
    """
    Validates the trading symbol.

    Rules:
    - Required (cannot be empty or None)
    - Must be a string
    - Must be entirely uppercase
    - Must be alphanumeric (no spaces or special characters)

    Args:
        symbol (str): The trading symbol to validate (e.g., 'BTCUSDT').

    Raises:
        SymbolValidationError: If the symbol fails any of the validation rules.
    """
    if not symbol:
        raise SymbolValidationError("Symbol is required and cannot be empty.")
    if not isinstance(symbol, str):
        raise SymbolValidationError(f"Symbol must be a string, got {type(symbol).__name__}.")
    if not symbol.isupper():
        raise SymbolValidationError(f"Symbol must be uppercase, got '{symbol}'.")
    if not symbol.isalnum():
        raise SymbolValidationError(f"Symbol must contain only alphanumeric characters, got '{symbol}'.")


def validate_side(side: Union[str, OrderSide]) -> None:
    """
    Validates the order side.

    Rules:
    - Must be a valid OrderSide (BUY, SELL)

    Args:
        side (Union[str, OrderSide]): The order side to validate.

    Raises:
        SideValidationError: If the side is invalid.
    """
    valid_sides = {s.value for s in OrderSide}
    side_value = side.value if isinstance(side, OrderSide) else side
    
    if side_value not in valid_sides:
        raise SideValidationError(f"Invalid side '{side_value}'. Must be one of {valid_sides}.")


def validate_order_type(order_type: Union[str, OrderType]) -> None:
    """
    Validates the order type.

    Rules:
    - Must be a valid OrderType

    Args:
        order_type (Union[str, OrderType]): The order type to validate.

    Raises:
        OrderTypeValidationError: If the order type is invalid.
    """
    valid_types = {t.value for t in OrderType}
    type_value = order_type.value if isinstance(order_type, OrderType) else order_type
    
    if type_value not in valid_types:
        raise OrderTypeValidationError(
            f"Invalid order type '{type_value}'. Must be one of {valid_types}."
        )


def validate_quantity(quantity: Union[int, float]) -> None:
    """
    Validates the order quantity.

    Rules:
    - Must be a number (int or float, strictly excluding bool)
    - Must be strictly positive (> 0)

    Args:
        quantity (Union[int, float]): The order quantity to validate.

    Raises:
        QuantityValidationError: If the quantity fails any validation rule.
    """
    if isinstance(quantity, bool):
        raise QuantityValidationError("Quantity cannot be a boolean.")
    if not isinstance(quantity, (int, float)):
        raise QuantityValidationError(
            f"Quantity must be a number, got {type(quantity).__name__}."
        )
    if quantity <= 0:
        raise QuantityValidationError(f"Quantity must be positive, got {quantity}.")


def validate_price(price: Optional[Union[int, float]], order_type: Union[str, OrderType]) -> None:
    """
    Validates the order price in the context of the order type.

    Rules:
    - Required if the order type is 'LIMIT' or 'STOP_LIMIT'
    - Must be a number (int or float, strictly excluding bool) if provided
    - Must be strictly positive (> 0) if provided

    Args:
        price (Optional[Union[int, float]]): The order price to validate.
        order_type (Union[str, OrderType]): The type of the order.

    Raises:
        PriceValidationError: If the price fails any validation rule.
    """
    type_value = order_type.value if isinstance(order_type, OrderType) else order_type
    
    if type_value in (OrderType.LIMIT.value, OrderType.STOP_LIMIT.value):
        if price is None:
            raise PriceValidationError(f"Price is required for {type_value} orders.")

    if price is not None:
        if isinstance(price, bool):
            raise PriceValidationError("Price cannot be a boolean.")
        if not isinstance(price, (int, float)):
            raise PriceValidationError(
                f"Price must be a number, got {type(price).__name__}."
            )
        if price <= 0:
            raise PriceValidationError(f"Price must be positive, got {price}.")


def validate_stop_price(stop_price: Optional[Union[int, float]], order_type: Union[str, OrderType]) -> None:
    """
    Validates the order stop price in the context of the order type.

    Rules:
    - Required if the order type is 'STOP_LIMIT'
    - Must be a number (int or float, strictly excluding bool) if provided
    - Must be strictly positive (> 0) if provided

    Args:
        stop_price (Optional[Union[int, float]]): The order stop price to validate.
        order_type (Union[str, OrderType]): The type of the order.

    Raises:
        StopPriceValidationError: If the stop price fails any validation rule.
    """
    type_value = order_type.value if isinstance(order_type, OrderType) else order_type
    
    if type_value == OrderType.STOP_LIMIT.value:
        if stop_price is None:
            raise StopPriceValidationError("Stop price is required for STOP_LIMIT orders.")

    if stop_price is not None:
        if isinstance(stop_price, bool):
            raise StopPriceValidationError("Stop price cannot be a boolean.")
        if not isinstance(stop_price, (int, float)):
            raise StopPriceValidationError(
                f"Stop price must be a number, got {type(stop_price).__name__}."
            )
        if stop_price <= 0:
            raise StopPriceValidationError(f"Stop price must be positive, got {stop_price}.")
