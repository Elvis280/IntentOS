from typing import Any, Dict, List
from app.world.models import WorldState
from app.context.models import ContextState, ReferencedObject
from app.context.tracker import ContextTracker
from app.context.history import HistoryManager
from app.context.resolver import ContextResolver

class ContextManager:
    """
    Orchestrates Tracker, History, and Resolver to maintain the current ContextState.
    Designed to be instantiated per-job (session scope), not as a global singleton.
    """
    def __init__(self):
        self.state = ContextState()
        self.tracker = ContextTracker()
        self.history = HistoryManager()
        self.resolver = ContextResolver()

    def update(self, goal: str, step: int, world_state: WorldState, recent_history_raw: List[Dict[str, Any]] = None) -> ContextState:
        # 1. Update execution metadata
        self.state.execution_goal = goal
        self.state.execution_step = step
        
        # 2. Sync History Manager if external history is provided
        # (Assuming the runtime passes the full job history here for simplicity)
        if recent_history_raw:
            # Re-sync rolling history for this iteration
            self.history.actions.clear()
            for entry in recent_history_raw[-self.history.max_size:]:
                action = entry.get("action", {})
                verified = entry.get("verified", True)
                self.history.add_action(action, verified)
                
        self.state.recent_actions = self.history.get_recent_actions()
        self.state.last_action = self.history.get_last_action()
        
        # Determine current selection from the last action (basic heuristic)
        last_action = self.state.last_action
        if last_action and last_action.get("action") and last_action["action"].get("action") == "CLICK":
            params = last_action["action"].get("parameters", {})
            self.state.current_selection = ReferencedObject(
                id=f"coord_{params.get('x', 0)}_{params.get('y', 0)}",
                type="ui_element",
                confidence=0.85,
                description="Recently clicked element"
            )
            
        # 3. Track deterministic changes from the objective World Model
        if world_state:
            updates = self.tracker.extract_context(world_state)
            for k, v in updates.items():
                setattr(self.state, k, v)
                
        # 4. Resolve semantic references ("this", "that") based on the current context
        if goal:
            resolved = self.resolver.resolve_references(goal, self.state)
            self.state.referenced_object = resolved
            
        return self.state
