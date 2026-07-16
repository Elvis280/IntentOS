import json
import os
from pathlib import Path
from pydantic import BaseModel, Field
from app.core.logger import logger

SETTINGS_FILE = Path.home() / ".intentos" / "settings.json"

class AppSettings(BaseModel):
    api_key: str = ""
    theme: str = "system"
    enable_voice: bool = True
    max_history_jobs: int = 50
    debug_mode: bool = False

class SettingsManager:
    def __init__(self):
        self.settings = self._load()

    def _load(self) -> AppSettings:
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return AppSettings(**data)
            except Exception as e:
                logger.error(f"[Settings] Error loading settings: {e}")
        return AppSettings()

    def save(self):
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            f.write(self.settings.model_dump_json(indent=2))

settings_manager = SettingsManager()
config = settings_manager.settings
