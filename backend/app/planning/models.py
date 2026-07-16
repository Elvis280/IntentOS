from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class PlanStepStatus(str, Enum):
    PENDING = "Pending"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    FAILED = "Failed"
    SKIPPED = "Skipped"
    WAITING = "Waiting"

class PlanStep(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    description: str
    objective: str
    expected_result: str
    priority: int = 1
    status: PlanStepStatus = PlanStepStatus.PENDING
    dependencies: List[str] = Field(default_factory=list)
    completion_condition: str

class ExecutionPlan(BaseModel):
    goal: str
    steps: List[PlanStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

class PlanProgress(BaseModel):
    current_step: Optional[str] = None
    completed_steps: int = 0
    failed_steps: int = 0
    skipped_steps: int = 0
    total_steps: int = 0
    percentage_complete: float = 0.0
    estimated_remaining_steps: int = 0
