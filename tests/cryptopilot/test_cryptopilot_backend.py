import pytest
from src.cryptopilot.trading.trading_engine import TradingEngine
from src.cryptopilot.portfolio.portfolio_manager import PortfolioManager
from src.cryptopilot.risk.risk_manager import RiskManager
from src.cryptopilot.analytics.market_data import MarketData

def test_trading_engine():
    engine = TradingEngine()
    order = engine.execute_trade("BTC/USD", "BUY", 1.5, 65000.0)
    assert order["status"] == "FILLED"
    assert order["symbol"] == "BTC/USD"
    assert order["amount"] == 1.5

def test_portfolio_manager():
    manager = PortfolioManager()
    balances = manager.get_balances()
    assert "USD" in balances
    assert "BTC" in balances
    manager.update_balance("BTC", 1.0)
    assert manager.get_balances()["BTC"] == 1.5

def test_risk_manager():
    manager = RiskManager()
    # 2.0 BTC @ 50k = 100k, portfolio = 200k. Position size = 50%, > 20% limit
    assert not manager.check_trade("BTC/USD", 2.0, 200000.0)
    # 0.5 BTC @ 50k = 25k, portfolio = 200k. Position size = 12.5%, < 20% limit
    assert manager.check_trade("BTC/USD", 0.5, 200000.0)

def test_market_data():
    md = MarketData()
    data = md.get_ticker("BTC/USD")
    assert data["symbol"] == "BTC/USD"
    assert data["trend"] == "bullish"
