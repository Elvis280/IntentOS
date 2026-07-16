from typing import Any, Dict, List
from app.schemas.verification import VerificationResult
from app.reflection.models import ReflectionResult

class RuntimeReflector:
    """
    Evaluates the VerificationResult and Runtime history deterministically
    to produce a ReflectionResult, suggesting memory updates or recovery.
    No LLM.
    """
    
    def reflect(self, verification: VerificationResult, history: List[Dict[str, Any]]) -> ReflectionResult:
        
        # 1. Analyze what happened
        success = verification.verified
        confidence = verification.confidence
        
        changes = []
        if verification.changed_world_objects.get("active_window"):
            changes.append("Active window changed.")
        if verification.changed_world_objects.get("applications", {}).get("added"):
            changes.append("New applications opened.")
        if verification.changed_ui_elements.get("added_elements"):
            changes.append("New UI elements detected.")
            
        summary = "Action executed successfully and produced expected changes." if success else "Action failed to produce expected changes."
        notes = verification.verification_reason
        
        # 2. Determine Memory Updates
        memory_updates = []
        if not success:
            memory_updates.append({
                "action": "remember",
                "key": "last_reflection_failure",
                "value": verification.verification_reason
            })
        else:
            memory_updates.append({
                "action": "forget",
                "key": "last_reflection_failure"
            })
            
        # 3. Determine if Recovery is required
        # For example, if the last two actions in history both failed verification.
        recovery_required = False
        
        # The history passed here does NOT include the current verification result yet,
        # so history[-1] is the previous action.
        if not success and len(history) > 0:
            last_entry = history[-1]
            # Since history now stores verification objects instead of just booleans
            was_last_verified = last_entry.get("verified", True)
            if type(was_last_verified) == bool:
                if not was_last_verified:
                    recovery_required = True
            else:
                # If it's a VerificationResult dict
                if not was_last_verified.get("verified", True):
                    recovery_required = True
                    
        return ReflectionResult(
            execution_summary=summary,
            confidence=confidence,
            success=success,
            discovered_changes=changes,
            runtime_notes=notes,
            memory_updates=memory_updates,
            recovery_required=recovery_required
        )
