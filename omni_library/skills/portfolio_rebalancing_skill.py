class PortfolioRebalancingSkill:
    """
    Skill to calculate necessary rebalancing trades.
    """
    def execute(self, current_balances: dict, target_allocations: dict) -> list:
        # Mock rebalancing
        trades = []
        for asset, target_pct in target_allocations.items():
            if current_balances.get(asset, 0) == 0:
                trades.append({"asset": asset, "action": "BUY_TO_TARGET", "target": target_pct})
        return trades
