"""
Working Memory package.

Provides a job-scoped, deterministic memory that is discarded
when the job finishes. No embeddings. No vector DBs. No LLM.
"""
from .models import WorkingMemoryState
from .manager import WorkingMemoryManager
