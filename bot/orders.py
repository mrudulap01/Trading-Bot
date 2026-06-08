import logging
from typing import Dict, Any, List, Union

from bot.client import BinanceFuturesClient
from bot.models import OrderResponse
from bot.constants import OrderSide, OrderType
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
    ValidationError
)

logger = logging.getLogger(__name__)


class OrderServiceError(Exception):
    """Custom exception raised when an order operation fails."""
    pass


class OrderService:
    """
    Service class responsible for coordinating order validation and execution.
    Implements clean architecture by taking the API client as a dependency
    and handling business logic around placing orders.
    """

    def __init__(self, client: BinanceFuturesClient) -> None:
        """
        Initializes the OrderService with a Binance client dependency.

        Args:
            client (BinanceFuturesClient): The configured Binance client for executing API calls.
        """
        self.client = client

    def place_market_order(self, symbol: str, side: Union[str, OrderSide], quantity: float) -> OrderResponse:
        """
        Validates inputs, logs the request, and places a market order.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
            side (str): The order side ('BUY' or 'SELL').
            quantity (float): The quantity to trade.

        Returns:
            Dict[str, Any]: A simplified order response.

        Raises:
            OrderServiceError: If validation fails or the API request errors out.
        """
        order_type = OrderType.MARKET
        try:
            logger.info(f"Validating MARKET order request - Symbol: {symbol}, Side: {side}, Qty: {quantity}")
            validate_symbol(symbol)
            validate_side(side)
            validate_order_type(order_type)
            validate_quantity(quantity)

            logger.info("Validation passed. Placing MARKET order...")
            raw_response = self.client.create_order(
                symbol=symbol,
                side=side.value if isinstance(side, OrderSide) else side,
                order_type=order_type.value,
                quantity=quantity
            )

            simplified_response = OrderResponse.from_binance_response(raw_response)
            logger.info(f"MARKET order successfully placed. Response: {simplified_response}")
            return simplified_response

        except ValidationError as e:
            logger.error(f"Validation failed for MARKET order: {e}")
            raise OrderServiceError(f"Market order validation error: {e}") from e
        except Exception as e:
            logger.error(f"Failed to place MARKET order via client: {e}")
            raise OrderServiceError(f"Market order execution error: {e}") from e

    def place_limit_order(self, symbol: str, side: Union[str, OrderSide], quantity: float, price: float) -> OrderResponse:
        """
        Validates inputs, logs the request, and places a limit order.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
            side (str): The order side ('BUY' or 'SELL').
            quantity (float): The quantity to trade.
            price (float): The limit price.

        Returns:
            Dict[str, Any]: A simplified order response.

        Raises:
            OrderServiceError: If validation fails or the API request errors out.
        """
        order_type = OrderType.LIMIT
        try:
            logger.info(f"Validating LIMIT order request - Symbol: {symbol}, Side: {side}, Qty: {quantity}, Price: {price}")
            validate_symbol(symbol)
            validate_side(side)
            validate_order_type(order_type)
            validate_quantity(quantity)
            validate_price(price, order_type)

            logger.info("Validation passed. Placing LIMIT order...")
            # Note: timeInForce='GTC' (Good Til Canceled) is required by Binance for limit orders
            raw_response = self.client.create_order(
                symbol=symbol,
                side=side.value if isinstance(side, OrderSide) else side,
                order_type=order_type.value,
                quantity=quantity,
                price=price,
                timeInForce="GTC"
            )

            simplified_response = OrderResponse.from_binance_response(raw_response)
            logger.info(f"LIMIT order successfully placed. Response: {simplified_response}")
            return simplified_response

        except ValidationError as e:
            logger.error(f"Validation failed for LIMIT order: {e}")
            raise OrderServiceError(f"Limit order validation error: {e}") from e
        except Exception as e:
            logger.error(f"Failed to place LIMIT order via client: {e}")
            raise OrderServiceError(f"Limit order execution error: {e}") from e

    def place_stop_limit_order(self, symbol: str, side: Union[str, OrderSide], quantity: float, price: float, stop_price: float) -> OrderResponse:
        """
        Validates inputs, logs the request, and places a stop limit order.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
            side (str): The order side ('BUY' or 'SELL').
            quantity (float): The quantity to trade.
            price (float): The limit price.
            stop_price (float): The stop price to trigger the limit order.

        Returns:
            Dict[str, Any]: A simplified order response.

        Raises:
            OrderServiceError: If validation fails or the API request errors out.
        """
        # In Binance Futures, a "Stop Limit" order is submitted as type "STOP"
        order_type = OrderType.STOP
        try:
            logger.info(f"Validating STOP_LIMIT order request - Symbol: {symbol}, Side: {side}, Qty: {quantity}, Price: {price}, Stop Price: {stop_price}")
            validate_symbol(symbol)
            validate_side(side)
            # We pass 'STOP_LIMIT' to our internal validator so it triggers the right checks
            validate_order_type(OrderType.STOP_LIMIT)
            validate_quantity(quantity)
            validate_price(price, OrderType.STOP_LIMIT)
            validate_stop_price(stop_price, OrderType.STOP_LIMIT)

            logger.info("Validation passed. Placing STOP_LIMIT order...")
            # Note: timeInForce='GTC' (Good Til Canceled) is required by Binance for limit orders
            raw_response = self.client.create_order(
                symbol=symbol,
                side=side.value if isinstance(side, OrderSide) else side,
                order_type=order_type.value,
                quantity=quantity,
                price=price,
                stopPrice=stop_price,
                timeInForce="GTC"
            )

            simplified_response = OrderResponse.from_binance_response(raw_response)
            logger.info(f"STOP_LIMIT order successfully placed. Response: {simplified_response}")
            return simplified_response

        except ValidationError as e:
            logger.error(f"Validation failed for STOP_LIMIT order: {e}")
            raise OrderServiceError(f"Stop Limit order validation error: {e}") from e
        except Exception as e:
            logger.error(f"Failed to place STOP_LIMIT order via client: {e}")
            
            # Catch the specific -1109 error for Testnet Algo Orders
            error_msg = str(e)
            if "-1109" in error_msg or "Invalid account" in error_msg:
                friendly_msg = (
                    "Binance Futures Testnet does not support Algo Orders (STOP_LIMIT) for this test account.\n"
                    "Please test MARKET and LIMIT orders, or test STOP_LIMIT on the Mainnet with real API keys."
                )
                raise OrderServiceError(friendly_msg) from e
                
            raise OrderServiceError(f"Stop Limit order execution error: {e}") from e

    def get_open_orders(self, symbol: str = None) -> List[OrderResponse]:
        """
        Retrieves all open orders, optionally filtered by symbol.
        """
        try:
            if symbol:
                validate_symbol(symbol)
                logger.info(f"Fetching open orders for {symbol}...")
                raw_orders = self.client.client.futures_get_open_orders(symbol=symbol)
            else:
                logger.info("Fetching all open orders...")
                raw_orders = self.client.client.futures_get_open_orders()
            
            return [OrderResponse.from_binance_response(o) for o in raw_orders]
        except ValidationError as e:
            raise OrderServiceError(f"Validation error: {e}") from e
        except Exception as e:
            logger.error(f"Failed to fetch open orders: {e}")
            raise OrderServiceError(f"Failed to fetch open orders: {e}") from e

    def get_order_history(self, symbol: str, limit: int = 50) -> List[OrderResponse]:
        """
        Retrieves the most recent order history for a specific symbol.
        """
        try:
            validate_symbol(symbol)
            logger.info(f"Fetching order history for {symbol} (limit {limit})...")
            raw_orders = self.client.client.futures_get_all_orders(symbol=symbol, limit=limit)
            return [OrderResponse.from_binance_response(o) for o in raw_orders]
        except ValidationError as e:
            raise OrderServiceError(f"Validation error: {e}") from e
        except Exception as e:
            logger.error(f"Failed to fetch order history: {e}")
            raise OrderServiceError(f"Failed to fetch order history: {e}") from e

    def get_current_price(self, symbol: str) -> float:
        """
        Retrieves the current market price for a symbol.
        """
        try:
            validate_symbol(symbol)
            logger.info(f"Fetching current price for {symbol}...")
            response = self.client.client.futures_symbol_ticker(symbol=symbol)
            return float(response.get("price", 0.0))
        except ValidationError as e:
            raise OrderServiceError(f"Validation error: {e}") from e
        except Exception as e:
            logger.error(f"Failed to fetch current price for {symbol}: {e}")
            raise OrderServiceError(f"Failed to fetch current price: {e}") from e

    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[List[Any]]:
        """
        Retrieves raw candlestick data for charting.
        Returns a list of lists: [Open time, Open, High, Low, Close, Volume, ...]
        """
        try:
            validate_symbol(symbol)
            logger.info(f"Fetching klines for {symbol} at {interval} interval...")
            return self.client.client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        except ValidationError as e:
            raise OrderServiceError(f"Validation error: {e}") from e
        except Exception as e:
            logger.error(f"Failed to fetch klines: {e}")
            raise OrderServiceError(f"Failed to fetch klines: {e}") from e

    def cancel_order(self, symbol: str, order_id: int) -> OrderResponse:
        """
        Cancels an active open order on Binance Futures.
        """
        try:
            validate_symbol(symbol)
            logger.info(f"Canceling order {order_id} for {symbol}...")
            raw_response = self.client.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            return OrderResponse.from_binance_response(raw_response)
        except ValidationError as e:
            raise OrderServiceError(f"Validation error: {e}") from e
        except Exception as e:
            logger.error(f"Failed to cancel order: {e}")
            raise OrderServiceError(f"Failed to cancel order: {e}") from e
