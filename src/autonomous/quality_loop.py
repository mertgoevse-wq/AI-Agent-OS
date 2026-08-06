import logging
from typing import List, Dict, Any
from src.execution.model_adapter import ModelAdapter

logger = logging.getLogger(__name__)

class QualityLoop:
    """
    Evaluates the output from the parallel executor.
    Simulates a Reviewer and QA/Testing agent.
    """
    def __init__(self, base_path: str = "C:/AI/Projects/AI-Agent-OS"):
        self.model_adapter = ModelAdapter(base_path=base_path)

    def evaluate_outputs(self, outputs: List[Dict[str, Any]], model: str = "gemini-1.5-flash") -> Dict[str, Any]:
        """
        Takes the results of the swarm execution and evaluates if they meet the criteria.
        Returns a dict indicating success and feedback.
        """
        # Combine all outputs into a single context for the reviewer
        combined_output = "\n".join([f"Agent: {out['agent_id']}\nResult: {out.get('output', out.get('error', 'None'))}" for out in outputs])
        
        # We simulate the Reviewer Agent
        messages = [
            {"role": "system", "content": "You are the QA and Reviewer Agent. Your job is to review the code/output of the engineering team. Reply ONLY with a JSON object containing two keys: 'passed' (boolean) and 'feedback' (string)."},
            {"role": "user", "content": f"Review this team output and determine if it solves the original task. Output:\n{combined_output}"}
        ]
        
        try:
            result_str = self.model_adapter.execute(model, messages)
            
            # Simple heuristic parse if model didn't return pure JSON
            passed = True
            if "false" in result_str.lower() or "passed\": false" in result_str.lower():
                passed = False
                
            return {
                "passed": passed,
                "feedback": result_str,
                "raw_review": result_str
            }
        except Exception as e:
            logger.error(f"Quality review failed: {e}")
            return {
                "passed": False,
                "feedback": f"Reviewer agent crashed: {e}"
            }
