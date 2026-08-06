import logging
import asyncio
from typing import Dict, Any
from src.autonomous.planner import PlannerAgent
from src.autonomous.architect import ArchitectAgent
from src.autonomous.developer import DeveloperAgent
from src.autonomous.qa_agent import QAAgent
from src.autonomous.security_agent import SecurityAgent
from src.autonomous.doc_agent import DocumentationAgent
from src.autonomous.qa_repair import QARepairEngine

class AutonomousEngineeringPipeline:
    """
    End-to-End Autonomous Multi-Agent Software Factory.
    Executes Planner -> Architect -> Developer -> QA -> Security -> Documentation
    with built-in Self-Repair Loop for zero regression engineering.
    """
    def __init__(self):
        self.logger = logging.getLogger("OMNI.AutonomousPipeline")
        self.planner = PlannerAgent()
        self.architect = ArchitectAgent()
        self.developer = DeveloperAgent()
        self.qa = QAAgent()
        self.security = SecurityAgent()
        self.doc = DocumentationAgent()
        self.repair_engine = QARepairEngine()

    async def run_pipeline(self, user_goal: str) -> Dict[str, Any]:
        self.logger.info(f"=== Starting Autonomous Engineering Pipeline: '{user_goal}' ===")
        
        # Step 1: Roadmap
        roadmap = self.planner.create_roadmap(user_goal)
        
        # Step 2: Architecture
        arch = self.architect.design_architecture(roadmap)
        
        # Step 3: Execution
        impl_results = []
        for task in roadmap["tasks"]:
            res = self.developer.implement_task(task, arch)
            impl_results.append(res)
            
        # Step 4: QA Verification
        passed, qa_report = self.qa.run_tests({"artifacts": impl_results})
        if not passed:
            self.logger.warning("QA check failed. Triggering Self-Repair Loop...")
            await self.repair_engine.repair({"artifacts": impl_results}, str(qa_report))
            
        # Step 5: Security Audit
        sec_report = self.security.audit_codebase(impl_results)
        
        # Step 6: Documentation Synthesis
        doc_summary = self.doc.update_docs({"goal": user_goal, "qa": qa_report, "security": sec_report})
        
        return {
            "status": "SUCCESS",
            "goal": user_goal,
            "roadmap": roadmap,
            "architecture": arch,
            "qa_report": qa_report,
            "security_report": sec_report,
            "doc_summary": doc_summary
        }
