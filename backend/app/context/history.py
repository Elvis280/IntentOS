from typing import Any, Dict, List

class HistoryManager:
    """
    Manages a bounded, rolling history of Runtime actions.
    Answers "What happened?" and "What object was modified?".
    """
    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.actions: List[Dict[str, Any]] = []
        
    def add_action(self, action: Dict[str, Any], verified: bool = True):
        entry = {
            "action": action,
            "verified": verified
        }
        self.actions.append(entry)
        if len(self.actions) > self.max_size:
            self.actions.pop(0)
            
    def get_recent_actions(self) -> List[Dict[str, Any]]:
        return list(self.actions)
        
    def get_last_action(self) -> Dict[str, Any]:
        return self.actions[-1] if self.actions else None
