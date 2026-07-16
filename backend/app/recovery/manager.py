from typing import Any, Dict, List
from app.recovery.models import RecoveryResult
from app.recovery.strategies import StrategyEngine
from app.schemas.verification import VerificationResult
from app.reflection.models import ReflectionResult

class RecoveryManager:
    """
    Orchestrates the Recovery phase.
    Maintains recovery_attempts state across the job.
    """
    
    def __init__(self):
        self._engine = StrategyEngine()
        self._recovery_attempts = 0
        
    def recover(
        self,
        verification: VerificationResult,
        reflection: ReflectionResult,
        last_action: Dict[str, Any]
    ) -> RecoveryResult:
        
        # Evaluate the strategy based on current failure count
        result = self._engine.evaluate(
            retry_count=self._recovery_attempts,
            verification=verification,
            reflection=reflection,
            last_action=last_action
        )
        
        # Increment internal tracker
        self._recovery_attempts = result.retry_count
        
        return result
        
    def reset_attempts(self):
        """Reset attempts when an action succeeds."""
        self._recovery_attempts = 0
