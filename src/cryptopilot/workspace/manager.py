import logging
from typing import Dict, Any

class WorkspaceManager:
    """
    Manages user workspaces, saved strategies, and dashboard presets.
    """
    def __init__(self):
        self.logger = logging.getLogger("CryptoPilot.Workspace")

    def get_workspace_config(self, user_id: str) -> Dict[str, Any]:
        return {
            "workspace_id": f"ws_{user_id}",
            "theme": "dark_glassmorphism",
            "default_pair": "BTC/USDT",
            "auto_rebalance": True,
            "risk_tolerance": "MODERATE"
        }
