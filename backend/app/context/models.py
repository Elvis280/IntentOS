from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ReferencedObject(BaseModel):
    """
    Represents an object semantically referenced in the goal (e.g., "this", "the selected image").
    """
    id: str
    type: str
    location: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    description: Optional[str] = None

class ContextState(BaseModel):
    """
    State of the user's current context. Describes what is relevant right now, independent of the World Model.
    """
    active_application: Optional[str] = None
    active_window_title: Optional[str] = None
    current_workspace: Optional[str] = None
    
    current_selection: Optional[ReferencedObject] = None
    referenced_object: Optional[ReferencedObject] = None
    
    last_action: Optional[Dict[str, Any]] = None
    recent_actions: List[Dict[str, Any]] = Field(default_factory=list)
    
    execution_goal: Optional[str] = None
    execution_step: int = 0
