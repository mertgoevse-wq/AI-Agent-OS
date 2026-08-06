import logging

logger = logging.getLogger(__name__)

class SelfImprovement:
    """
    Handles adjusting the workflow or prompting if the QualityLoop fails.
    """
    def __init__(self, memory):
        self.memory = memory
        
    def adjust_for_retry(self, plan: dict, review_feedback: dict) -> dict:
        """
        Modifies the plan based on the feedback from the Reviewer agent to try again.
        """
        logger.info("Self-improvement cycle triggered. Adjusting plan...")
        
        # Log the failure to memory
        self.memory.append_log(f"Attempt failed. Feedback: {review_feedback.get('feedback', '')}")
        
        # We adjust the sub-tasks by appending the feedback so agents know what to fix
        for sub_task in plan.get("sub_tasks", []):
            original_task = sub_task.get("task", "")
            feedback_str = review_feedback.get("feedback", "")
            sub_task["task"] = f"{original_task}\n\nPREVIOUS ATTEMPT FAILED. FEEDBACK TO FIX: {feedback_str}"
            
        return plan
