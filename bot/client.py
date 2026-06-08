import os
import logging
from typing import Dict, Any, Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from bot.config import BotConfig

# Initialize module logger
logger = logging.getLogger(__name__)


class BinanceFuturesClient:
    """
    Wrapper class for the Binance Futures Testnet API client.
    
    This class handles the initialization of the python-binance Client
    specifically for the Binance Futures Testnet, and provides focused
    methods for basic API communication.
    """

    def __init__(self, config: Optional[BotConfig] = None) -> None:
        """
        Initializes the Binance Futures client using the provided configuration.
        If no configuration is provided, it attempts to load from the environment.
        
        Args:
            config (Optional[BotConfig]): The configuration object.
            
        Raises:
            ValueError: If configuration is invalid or missing.
        """
        self.config = config or BotConfig.load_from_env()

        try:
            # Setting testnet=True routes both spot and futures calls to their respective testnets.
            self.client = Client(
                self.config.api_key, 
                self.config.api_secret, 
                testnet=self.config.is_testnet
            )
            logger.info("Binance client initialized for Futures Testnet.")
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Tests the connection to the Binance Futures API by pinging the server.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            self.client.futures_ping()
            logger.info("Successfully connected to Binance Futures Testnet.")
            return True
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Connection test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection test: {e}")
            return False

    def verify_credentials(self) -> Dict[str, bool]:
        """
        Verifies API credentials by requesting account information from a signed endpoint.
        This confirms whether the keys are valid and possess Futures trading permissions.

        Returns:
            Dict[str, bool]: A dictionary containing the status of various checks:
                - api_key_valid
                - secret_key_valid
                - futures_permissions
                - account_reachable
        """
        status = {
            "api_key_valid": False,
            "secret_key_valid": False,
            "futures_permissions": False,
            "account_reachable": False
        }
        
        try:
            # futures_account() is a signed endpoint requiring valid keys and futures permissions
            account_info = self.client.futures_account()
            
            # If the call succeeds, all criteria are met
            status["api_key_valid"] = True
            status["secret_key_valid"] = True
            status["futures_permissions"] = account_info.get("canTrade", False)
            status["account_reachable"] = True
            
            logger.info("Credentials verified successfully via futures_account().")
            
        except BinanceAPIException as e:
            logger.error(f"Credential verification failed with API Exception: {e.status_code} - {e.message}")
            if e.code == -2015:
                # -2015: Invalid API-key, IP, or permissions for action
                status["account_reachable"] = True  # We reached Binance API
                status["api_key_valid"] = False
                status["secret_key_valid"] = False
                status["futures_permissions"] = False
        except BinanceRequestException as e:
            logger.error(f"Credential verification failed with Request Exception: {e}")
            status["account_reachable"] = False
        except Exception as e:
            logger.error(f"Unexpected error during credential verification: {e}")
            status["account_reachable"] = False
            
        return status

    def get_server_time(self) -> Optional[int]:
        """
        Retrieves the current server time from Binance Futures.

        Returns:
            Optional[int]: The server time in milliseconds, or None if the request fails.
        """
        try:
            server_time_info = self.client.futures_time()
            return server_time_info.get("serverTime")
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Failed to retrieve server time: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving server time: {e}")
            return None

    def create_order(
        self, symbol: str, side: str, order_type: str, quantity: float, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Creates an order on the Binance Futures Testnet.
        
        Note: Order validation is not handled here and should be performed 
        before calling this method.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
            side (str): The order side ('BUY' or 'SELL').
            order_type (str): The order type (e.g., 'MARKET', 'LIMIT').
            quantity (float): The quantity of the asset to trade.
            **kwargs: Additional optional parameters for the order (e.g., price, timeInForce).

        Returns:
            Dict[str, Any]: The order response dictionary from Binance.

        Raises:
            BinanceAPIException: If Binance API returns an error.
            BinanceRequestException: If the request to Binance fails.
            Exception: For any other unexpected errors.
        """
        try:
            order_response = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity,
                **kwargs
            )
            order_id = order_response.get("orderId", "UNKNOWN")
            logger.info(f"Order created successfully for {symbol}: ID {order_id}")
            return order_response
        except BinanceAPIException as e:
            logger.error(f"Binance API Exception while creating order: {e.status_code} - {e.message}")
            raise
        except BinanceRequestException as e:
            logger.error(f"Binance Request Exception while creating order: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating order: {e}")
            raise
