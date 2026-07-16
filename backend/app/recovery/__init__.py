"""
Recovery Engine package.

Executes after Reflection if a recovery is required.
Selects deterministic strategies to retry, modify, ask the user, or abort.
"""
from .models import RecoveryStrategy, RecoveryResult
from .manager import RecoveryManager
