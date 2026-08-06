import pytest
from src.cryptopilot.portfolio.intelligence import PortfolioIntelligenceEngine
from src.cryptopilot.risk.engine import RiskEngine
from src.cryptopilot.analytics.engine import MarketAnalyticsEngine
from src.cryptopilot.auth.manager import AuthManager
from src.cryptopilot.workspace.manager import WorkspaceManager
from src.cryptopilot.assistant.service import CryptoCopilotAssistant

def test_portfolio_intelligence():
    engine = PortfolioIntelligenceEngine()
    summary = engine.get_portfolio_summary()
    assert summary["total_balance_usd"] > 0
    assert len(summary["allocation"]) == 4

def test_risk_engine():
    risk = RiskEngine()
    eval_res = risk.evaluate_risk({})
    assert eval_res["risk_score"] == "MODERATE"
    assert eval_res["value_at_risk_pct"] > 0

def test_market_analytics():
    analytics = MarketAnalyticsEngine()
    metrics = analytics.get_market_metrics()
    assert metrics["sentiment_score"] > 50
    assert metrics["market_phase"] == "BULLISH_ACCUMULATION"

def test_auth_manager():
    auth = AuthManager()
    user = auth.authenticate_user("trader_pro", "hash_123")
    assert user["role"] == "TRADER_ADMIN"
    assert user["session_token"].startswith("cp_sess_")

def test_workspace_manager():
    ws = WorkspaceManager()
    config = ws.get_workspace_config("usr_trader")
    assert config["default_pair"] == "BTC/USDT"
    assert config["auto_rebalance"] == True

def test_crypto_copilot_assistant():
    assistant = CryptoCopilotAssistant()
    res = assistant.process_query("What is the current portfolio risk?")
    assert "VaR" in res["response"]
