"""
Progress tracker.

Calculates metrics for the current execution plan.
"""
from app.planning.models import ExecutionPlan, PlanProgress, PlanStepStatus

class ProgressTracker:
    
    def calculate(self, plan: ExecutionPlan) -> PlanProgress:
        if not plan or not plan.steps:
            return PlanProgress()
            
        total = len(plan.steps)
        completed = sum(1 for s in plan.steps if s.status == PlanStepStatus.COMPLETED)
        failed = sum(1 for s in plan.steps if s.status == PlanStepStatus.FAILED)
        skipped = sum(1 for s in plan.steps if s.status == PlanStepStatus.SKIPPED)
        
        active = next((s.id for s in plan.steps if s.status == PlanStepStatus.ACTIVE), None)
        
        pct = (completed / total) if total > 0 else 0.0
        remaining = total - (completed + failed + skipped)
        
        return PlanProgress(
            current_step=active,
            completed_steps=completed,
            failed_steps=failed,
            skipped_steps=skipped,
            total_steps=total,
            percentage_complete=round(pct, 4),
            estimated_remaining_steps=max(0, remaining)
        )
