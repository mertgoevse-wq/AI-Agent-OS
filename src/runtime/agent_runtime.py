"""Agent Runtime Engine

The core execution environment for agents in the OMNI-Agent-Swarm.
Handles loading, context injection, and strict permission checking.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AgentRuntimeEngine:
    """Executes a single agent within a strict security boundary."""
    
    def __init__(self, agent_registry, skill_registry, prompt_registry, memory_manager, model_router):
        self.agent_registry = agent_registry
        self.skill_registry = skill_registry
        self.prompt_registry = prompt_registry
        self.memory_manager = memory_manager
        self.model_router = model_router
        
    async def execute(self, agent_id: str, task: str, context: Dict[str, Any]) -> str:
        """Executes a task for a specific agent with full context."""
        # Mock loading for now as agent_registry structure may vary
        tier = "pro_high" if "architect" in agent_id or "researcher" in agent_id else "flash"
        agent_def = {"id": agent_id, "role": agent_id, "model_tier": tier, "allowed_skills": ["code_analysis"]}
        logger.info(f"Loaded agent: {agent_id}")
        
        # 2. Inject Prompt & Context
        system_prompt = self.prompt_registry.get_prompt(agent_id, context=context)
        
        # 3. Add Memory
        stm_context = self.memory_manager.get_short_term_memory(agent_id)
        
        # 4. Load Allowed Skills
        allowed_tools = [
            skill for skill in agent_def.get("allowed_skills", [])
            if self.skill_registry.has_skill(skill)
        ]
        
        logger.info(f"Agent {agent_id} initialized with {len(allowed_tools)} tools.")
        
        # 5. Route to LLM and execute
        result = await self.model_router.route_and_execute(
            model_tier=agent_def["model_tier"],
            prompt=system_prompt,
            task=task,
            memory=stm_context,
            tools=allowed_tools
        )
        
        # 6. Save to Memory
        self.memory_manager.save_to_history(agent_id, task, result)
        
        return result
