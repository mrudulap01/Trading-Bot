import os
from dataclasses import dataclass
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

@dataclass
class BotConfig:
    """
    Centralized configuration for the Trading Bot.
    Uses dataclass to strictly type configurations loaded from environment variables.
    """
    api_key: str
    api_secret: str
    is_testnet: bool = True

    @classmethod
    def load_from_env(cls) -> "BotConfig":
        """
        Loads configuration from the environment and validates required fields.

        Returns:
            BotConfig: An instantiated and validated configuration object.
            
        Raises:
            ValueError: If required credentials are missing.
        """
        load_dotenv()
        
        api_key = os.environ.get("API_KEY")
        api_secret = os.environ.get("API_SECRET")

        if not api_key or not api_secret:
            logger.error("API_KEY or API_SECRET environment variables are missing.")
            raise ValueError("API_KEY and API_SECRET must be set in environment variables.")

        # Defaulting to True for the assignment scope
        is_testnet = os.environ.get("TESTNET", "True").lower() in ("true", "1", "yes")

        logger.info("Bot configuration loaded securely.")
        return cls(
            api_key=api_key,
            api_secret=api_secret,
            is_testnet=is_testnet
        )
