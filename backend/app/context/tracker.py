from typing import Any, Dict
from app.world.models import WorldState

class ContextTracker:
    """
    Extracts deterministic context from available information (like the WorldState).
    Avoids making speculative assumptions.
    """
    def extract_context(self, world: WorldState) -> Dict[str, Any]:
        updates = {}
        
        # Extract active window directly from WorldState
        if world.active_window:
            updates['active_window_title'] = world.active_window
            
            # Simple heuristic to extract application from typical "Document - Application" window titles
            parts = world.active_window.split(" - ")
            if len(parts) > 1:
                updates['active_application'] = parts[-1].strip()
            else:
                updates['active_application'] = world.active_window.strip()
                
            updates['current_workspace'] = updates['active_application']
            
        return updates
