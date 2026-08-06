import logging

class RiskManager:
    """
    Enforces risk constraints before trades can be executed.
    """
    def __init__(self, max_drawdown: float = 0.15, max_position_size: float = 0.20):
        self.logger = logging.getLogger("CryptoPilot.Risk")
        self.max_drawdown = max_drawdown
        self.max_position_size = max_position_size

    def check_trade(self, symbol: str, amount: float, current_portfolio_value: float) -> bool:
        """
        Validates if a trade exceeds risk bounds.
        """
        # Simplistic mock check
        trade_value = amount * 50000 # Mock price
        if trade_value > current_portfolio_value * self.max_position_size:
            self.logger.warning(f"Trade for {symbol} exceeds max position size!")
            return False
        return True
