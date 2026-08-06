import logging
from typing import Dict, Any

class MarketData:
    """
    Fetches market analytics (mocked).
    """
    def __init__(self):
        self.logger = logging.getLogger("CryptoPilot.Analytics")

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Returns mock ticker data.
        """
        return {
            "symbol": symbol,
            "price": 65000.0 if "BTC" in symbol else 3500.0,
            "volume_24h": 1500000.0,
            "trend": "bullish"
        }
