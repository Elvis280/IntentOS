from typing import Any, Dict, List
from app.schemas.verification import VerificationResult
from app.reflection.models import ReflectionResult
from app.reflection.reflector import RuntimeReflector

class ReflectionManager:
    """
    Orchestrates the Reflection phase.
    Instantiated per-job in the runtime loop.
    """
    
    def __init__(self):
        self._reflector = RuntimeReflector()
        
    def reflect(self, verification: VerificationResult, history: List[Dict[str, Any]]) -> ReflectionResult:
        """
        Run the reflection logic to evaluate verification and history.
        """
        return self._reflector.reflect(verification, history)
