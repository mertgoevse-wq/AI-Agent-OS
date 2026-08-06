import logging
from typing import Dict

class PortfolioManager:
    """
    Manages asset allocation and balances.
    """
    def __init__(self):
        self.logger = logging.getLogger("CryptoPilot.Portfolio")
        # Mock initial balances
        self.balances = {
            "USD": 100000.0,
            "BTC": 0.5,
            "ETH": 10.0
        }

    def get_balances(self) -> Dict[str, float]:
        return self.balances

    def update_balance(self, asset: str, delta: float):
        if asset not in self.balances:
            self.balances[asset] = 0.0
        self.balances[asset] += delta
        self.logger.info(f"Updated {asset} balance to {self.balances[asset]}")
