import logging
import json
from src.autonomous.task_planner import TaskPlanner
from src.autonomous.parallel_executor import ParallelExecutor
from src.autonomous.quality_loop import QualityLoop
from src.autonomous.agent_memory import AgentMemory
from src.autonomous.self_improvement import SelfImprovement

logger = logging.getLogger(__name__)

class AutonomousOrchestrator:
    """
    The main autonomous loop for OMNI AI-Agent-OS.
    Manages the lifecycle: Task -> Plan -> Parallel Execute -> Quality Review -> Self Improve.
    """
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.planner = TaskPlanner(base_path=base_path)
        self.executor = ParallelExecutor(base_path=base_path)
        self.quality_loop = QualityLoop(base_path=base_path)
        self.memory = AgentMemory(base_path=base_path)
        self.improver = SelfImprovement(self.memory)
        
    def run(self, user_request: str, max_iterations: int = 3) -> dict:
        """
        Runs the full autonomous loop for a given request.
        """
        logger.info(f"Starting Autonomous Loop for task: {user_request}")
        
        # 1. Plan
        plan = self.planner.plan_task(user_request)
        logger.info(f"Generated Plan: {json.dumps(plan, indent=2)}")
        self.memory.update_key("current_plan", plan)
        
        iteration = 0
        final_results = None
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"--- Iteration {iteration} ---")
            self.memory.append_log(f"Starting iteration {iteration}")
            
            # 2. Parallel Execute
            # Build the shared context from memory
            shared_context = f"Global Task: {user_request}\nPrevious Logs: {self.memory.get_key('execution_logs', [])}"
            
            results = self.executor.run_sync(plan.get("sub_tasks", []), shared_context, plan.get("recommended_model", "gemini-1.5-flash"))
            
            # 3. Quality Review
            review = self.quality_loop.evaluate_outputs(results, model=plan.get("recommended_model", "gemini-1.5-flash"))
            
            if review.get("passed", False):
                logger.info("Quality review passed!")
                self.memory.append_log(f"Iteration {iteration} success.")
                final_results = {
                    "status": "success",
                    "iterations": iteration,
                    "plan": plan,
                    "agent_outputs": results,
                    "review": review
                }
                break
            else:
                logger.warning(f"Quality review failed: {review.get('feedback', '')}")
                # 4. Self Improve
                if iteration < max_iterations:
                    plan = self.improver.adjust_for_retry(plan, review)
                else:
                    final_results = {
                        "status": "failed",
                        "iterations": iteration,
                        "plan": plan,
                        "agent_outputs": results,
                        "review": review
                    }
                    
        return final_results
