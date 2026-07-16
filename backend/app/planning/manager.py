from typing import Optional
from app.core.logger import logger
from app.planning.models import ExecutionPlan, PlanStep, PlanStepStatus
from app.planning.planner import Planner
from app.planning.progress import ProgressTracker

class PlanManager:
    """
    Orchestrates the active plan and handles step transitions.
    """
    def __init__(self):
        self._planner = Planner()
        self._tracker = ProgressTracker()
        self._plan: Optional[ExecutionPlan] = None
        
    def initialize(self, goal: str, world: dict, context: dict) -> None:
        self._plan = self._planner.create_plan(goal, world, context)
        if self._plan.steps:
            self._plan.steps[0].status = PlanStepStatus.ACTIVE
            
    def get_plan(self) -> Optional[ExecutionPlan]:
        return self._plan
        
    def get_progress(self):
        return self._tracker.calculate(self._plan)
        
    def get_active_step(self) -> Optional[PlanStep]:
        if not self._plan:
            return None
        for step in self._plan.steps:
            if step.status == PlanStepStatus.ACTIVE:
                return step
        return None
        
    def mark_step_completed(self) -> bool:
        """Marks the current active step as completed and activates the next one. Returns True if plan is fully completed."""
        active = self.get_active_step()
        if active:
            active.status = PlanStepStatus.COMPLETED
            
            # Find next pending
            for step in self._plan.steps:
                if step.status == PlanStepStatus.PENDING:
                    step.status = PlanStepStatus.ACTIVE
                    return False
        return True
        
    def mark_step_failed_and_replan(self, world: dict, context: dict) -> bool:
        """Marks the current active step as failed, and requests an alternative step. Returns True if successfully replanned."""
        active = self.get_active_step()
        if active:
            active.status = PlanStepStatus.FAILED
            try:
                alt_step = self._planner.replan(self._plan.goal, active, world, context)
                alt_step.status = PlanStepStatus.ACTIVE
                # Insert the new step right after the failed one
                idx = self._plan.steps.index(active)
                self._plan.steps.insert(idx + 1, alt_step)
                return True
            except Exception as e:
                logger.error(f"[Planner] Failed to replan: {e}")
                return False
        return False
