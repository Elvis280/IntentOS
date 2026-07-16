"""
Voice Runtime package.

Handles Wake Word -> Speech-To-Text -> Intent parsing.
Spawns background jobs in the Runtime once an intent is identified.
"""
from .manager import VoiceManager
