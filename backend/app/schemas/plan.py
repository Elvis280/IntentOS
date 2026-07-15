from pydantic import BaseModel
from typing import List, Optional


class PlanStep(BaseModel):
    step: int
    action: str
    target: Optional[str] = None
    description: str
    expected_result: str


class TaskPlan(BaseModel):
    goal: str
    steps: List[PlanStep]
