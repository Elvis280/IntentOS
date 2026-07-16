from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class RecoveryStrategy(str, Enum):
    RETRY = "Retry"
    WAIT_AND_RETRY = "Wait and Retry"
    MODIFY_ACTION = "Modify Action"
    ASK_USER = "Ask User"
    ABORT = "Abort"

class RecoveryResult(BaseModel):
    should_continue: bool
    strategy: RecoveryStrategy
    retry_count: int
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    
    modified_action: Optional[Dict[str, Any]] = None
    user_clarification_required: bool = False
    clarification_question: Optional[str] = None
    
    runtime_notes: str
    timestamp: datetime = Field(default_factory=datetime.now)
