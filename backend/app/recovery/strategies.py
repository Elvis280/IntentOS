"""
Recovery Strategies.

A deterministic rules engine evaluating the current state to determine
the optimal recovery path. No LLM calls.
"""
from typing import Any, Dict
from app.recovery.models import RecoveryStrategy, RecoveryResult
from app.schemas.verification import VerificationResult
from app.reflection.models import ReflectionResult

class StrategyEngine:
    """
    Evaluates failure states and determines the recovery strategy.
    """
    
    def evaluate(
        self,
        retry_count: int,
        verification: VerificationResult,
        reflection: ReflectionResult,
        last_action: Dict[str, Any]
    ) -> RecoveryResult:
        
        act_type = last_action.get("action", "")
        
        # 1. First failure
        if retry_count == 0:
            if act_type in ("OPEN_URL", "OPEN_APPLICATION", "WAIT"):
                # These operations often take time, let's inject a wait
                modified = {"action": "WAIT", "parameters": {"seconds": 2}, "thought": "Recovery: waiting for operation to complete."}
                return RecoveryResult(
                    should_continue=True,
                    strategy=RecoveryStrategy.WAIT_AND_RETRY,
                    retry_count=1,
                    confidence=0.9,
                    explanation="Operation might be delayed. Waiting before proceeding.",
                    modified_action=modified,
                    runtime_notes="Injected WAIT action."
                )
            else:
                # Simple retry for clicks/typing
                return RecoveryResult(
                    should_continue=True,
                    strategy=RecoveryStrategy.RETRY,
                    retry_count=1,
                    confidence=0.8,
                    explanation="Transient failure. Retrying the exact action.",
                    modified_action=last_action,
                    runtime_notes="Replaying last action."
                )
                
        # 2. Second failure
        if retry_count == 1:
            if act_type == "CLICK":
                # Slightly adjust coordinates
                params = last_action.get("parameters", {})
                new_params = dict(params)
                if "x" in new_params and "y" in new_params:
                    # Nudge by a few pixels
                    new_params["y"] = new_params["y"] + 5
                
                modified = {"action": "CLICK", "parameters": new_params, "thought": "Recovery: Adjusted click coordinates."}
                return RecoveryResult(
                    should_continue=True,
                    strategy=RecoveryStrategy.MODIFY_ACTION,
                    retry_count=2,
                    confidence=0.7,
                    explanation="Click failed. Nudging coordinates slightly.",
                    modified_action=modified,
                    runtime_notes="Adjusted click Y+5."
                )
            
            # If not a click, maybe just wait and retry
            modified = {"action": "WAIT", "parameters": {"seconds": 2}, "thought": "Recovery: Second attempt, waiting."}
            return RecoveryResult(
                should_continue=True,
                strategy=RecoveryStrategy.WAIT_AND_RETRY,
                retry_count=2,
                confidence=0.75,
                explanation="Second failure. Waiting before next step.",
                modified_action=modified,
                runtime_notes="Injected WAIT action."
            )
                
        # 3. Third failure - Ask User
        if retry_count == 2:
            return RecoveryResult(
                should_continue=False,  # Pause execution
                strategy=RecoveryStrategy.ASK_USER,
                retry_count=3,
                confidence=0.4,
                explanation="Multiple failures detected. Ambiguity is high.",
                user_clarification_required=True,
                clarification_question="The last action failed multiple times. How should I proceed?",
                runtime_notes="Requesting user clarification."
            )
            
        # 4. Abort
        return RecoveryResult(
            should_continue=False,
            strategy=RecoveryStrategy.ABORT,
            retry_count=retry_count + 1,
            confidence=1.0,
            explanation="Retry limit exceeded.",
            runtime_notes="Aborting due to consecutive failures."
        )
