from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ReflectionResult(BaseModel):
    """
    Structured outcome of the Reflection phase.
    Evaluates what happened, whether progress was made, and requests memory updates.
    """
    execution_summary: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    success: bool
    
    discovered_changes: List[str] = Field(default_factory=list)
    runtime_notes: str
    
    # Emits requests to the Working Memory Manager (e.g. {'action': 'remember', 'key': 'last_error', 'value': '...'})
    memory_updates: List[Dict[str, Any]] = Field(default_factory=list)
    
    recovery_required: bool = False
