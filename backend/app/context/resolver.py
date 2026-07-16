import re
from typing import Optional
from app.context.models import ReferencedObject, ContextState

class ContextResolver:
    """
    Resolves semantic references in the goal (e.g., "this", "it") into structured
    context objects without modifying the original goal.
    """
    
    REFERENCE_WORDS = {"this", "that", "it", "the selected"}
    
    def resolve_references(self, goal: str, state: ContextState) -> Optional[ReferencedObject]:
        goal_lower = goal.lower()
        
        # Check if the goal uses a reference word
        uses_reference = any(re.search(rf"\b{word}\b", goal_lower) for word in self.REFERENCE_WORDS)
        
        if uses_reference and state.current_selection:
            # We found a reference word and we have a current selection
            # We return a cloned ReferencedObject representing the resolution, with a confidence score.
            return ReferencedObject(
                id=state.current_selection.id,
                type=state.current_selection.type,
                location=state.current_selection.location,
                description=state.current_selection.description,
                confidence=0.94 # High confidence since we have a direct selection match
            )
            
        if uses_reference and not state.current_selection:
            # Goal uses a reference but we don't have a selection
            # In a more advanced version, this could use an LLM or look at active window.
            # For now, return a low confidence placeholder or None
            return None
            
        return None
