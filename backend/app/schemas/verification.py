from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class VerificationResult(BaseModel):
    """
    Structured outcome of the Verification phase.
    """
    verified: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    summary: str
    
    expected_action: Dict[str, Any]
    executed_action: Dict[str, Any]
    
    changed_world_objects: Dict[str, Any] = Field(default_factory=dict)
    changed_ui_elements: Dict[str, Any] = Field(default_factory=dict)
    changed_context: Dict[str, Any] = Field(default_factory=dict)
    
    verification_reason: str
    recommended_recovery: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
