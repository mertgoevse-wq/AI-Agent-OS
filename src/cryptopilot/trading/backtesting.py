import logging
from typing import List, Dict

class BacktestingFramework:
    """
    Runs historical simulation modes for evaluating AI trading strategies.
    """
    def __init__(self, strategy_engine):
        self.logger = logging.getLogger("CryptoPilot.Backtesting")
        self.strategy_engine = strategy_engine

    def run_simulation(self, historical_data: List[Dict], initial_capital: float = 100000.0) -> dict:
        """
        Simulates strategy execution over historical data.
        """
        self.logger.info("Starting backtest simulation...")
        capital = initial_capital
        
        for snapshot in historical_data:
            signals = self.strategy_engine.evaluate_market(snapshot)
            for signal in signals:
                if signal["action"] == "BUY":
                    capital *= 1.05 # Mock 5% profit per buy signal
                elif signal["action"] == "SELL":
                    capital *= 0.98 # Mock 2% loss protection

        roi = ((capital - initial_capital) / initial_capital) * 100
        return {
            "initial_capital": initial_capital,
            "final_capital": capital,
            "roi_percent": round(roi, 2)
        }
