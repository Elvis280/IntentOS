from typing import Any, Dict, List
from app.schemas.verification import VerificationResult

class Verifier:
    """
    Enhanced Verifier (Sprint 5 Part 2).
    Compares World, UI, and Context state deterministically to assess execution outcome.
    """
    
    IGNORED_WORLD_FIELDS = {"timestamp", "summary"}

    def _comparable_dict(self, state: dict, ignore_fields: set) -> dict:
        """Return state dict with volatile fields stripped out."""
        return {k: v for k, v in state.items() if k not in ignore_fields}

    def _diff_lists(self, before: list, after: list) -> Dict[str, list]:
        """Simple set-based diff for string lists."""
        b_set = set(before)
        a_set = set(after)
        return {
            "added": list(a_set - b_set),
            "removed": list(b_set - a_set)
        }

    def _diff_ui(self, before: List[Dict[str, Any]], after: List[Dict[str, Any]]) -> Dict[str, list]:
        """Diff UI elements based on type and text to find substantive changes."""
        # Create a simplified representation of elements for diffing
        def _simplify(ui_list):
            return set(f"{e.get('type')}:{e.get('text')}" for e in ui_list if e.get('text'))
            
        b_set = _simplify(before)
        a_set = _simplify(after)
        
        return {
            "added_elements": list(a_set - b_set),
            "removed_elements": list(b_set - a_set)
        }

    def verify(
        self, 
        before_world: dict, 
        after_world: dict, 
        before_ui: list, 
        after_ui: list,
        before_context: dict,
        after_context: dict,
        action: dict
    ) -> VerificationResult:

        # 1. Compute deterministic diffs
        changed_world = {}
        
        bw = self._comparable_dict(before_world, self.IGNORED_WORLD_FIELDS)
        aw = self._comparable_dict(after_world, self.IGNORED_WORLD_FIELDS)
        
        if bw.get("active_window") != aw.get("active_window"):
            changed_world["active_window"] = {"before": bw.get("active_window"), "after": aw.get("active_window")}
            
        changed_world["applications"] = self._diff_lists(bw.get("applications", []), aw.get("applications", []))
        changed_world["text"] = self._diff_lists(bw.get("text", []), aw.get("text", []))
        
        changed_ui = self._diff_ui(before_ui, after_ui)
        
        changed_context = {}
        if before_context.get("current_workspace") != after_context.get("current_workspace"):
            changed_context["current_workspace"] = {"before": before_context.get("current_workspace"), "after": after_context.get("current_workspace")}

        # 2. Evaluate outcome based on action type
        verified = False
        reason = "No measurable changes detected."
        confidence = 0.5
        
        act = action.get("action")
        
        if act == "OPEN_URL":
            if changed_world.get("active_window"):
                verified = True
                reason = "Active window changed after opening URL."
                confidence = 0.9
            elif changed_world["text"]["added"]:
                verified = True
                reason = "New text appeared on screen after opening URL."
                confidence = 0.7

        elif act == "OPEN_APPLICATION":
            if changed_world["applications"]["added"]:
                verified = True
                reason = f"New application opened: {changed_world['applications']['added']}"
                confidence = 0.95
            elif changed_world.get("active_window"):
                verified = True
                reason = "Active window changed."
                confidence = 0.7

        elif act == "CLICK":
            if changed_world.get("active_window") or changed_ui["added_elements"] or changed_world["text"]["added"]:
                verified = True
                reason = "UI or window state changed after click."
                confidence = 0.85
            else:
                reason = "Click produced no observable UI changes."
                confidence = 0.8

        elif act == "TYPE":
            if changed_world["text"]["added"] or changed_ui["added_elements"]:
                verified = True
                reason = "New text/elements detected after typing."
                confidence = 0.85
            else:
                reason = "Typing produced no observable changes."
                confidence = 0.8
                
        elif changed_world.get("active_window") or changed_world.get("applications", {}).get("added") or changed_world.get("text", {}).get("added") or changed_ui.get("added_elements") or changed_context:
            verified = True
            reason = f"Action {act} resulted in substantive measurable changes to World/UI."
            confidence = 0.85
            
        else:
            # PRESS_KEY, WAIT, SCROLL — assume success unless we have specific strict checks
            verified = True
            reason = f"Action {act} assumed successful (no strict verification criteria)."
            confidence = 0.6

        return VerificationResult(
            verified=verified,
            confidence=confidence,
            summary="Verification Passed" if verified else "Verification Failed",
            expected_action=action,
            executed_action=action,
            changed_world_objects=changed_world,
            changed_ui_elements=changed_ui,
            changed_context=changed_context,
            verification_reason=reason,
            recommended_recovery="Retry action with different parameters." if not verified else None
        )

verifier = Verifier()