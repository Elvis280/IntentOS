"""
Reflection package.

Runs immediately after verification to determine what happened, 
whether the Runtime expectation was correct, and whether Memory/Recovery
should be activated. Deterministic only. No LLMs.
"""
from .models import ReflectionResult
from .manager import ReflectionManager
