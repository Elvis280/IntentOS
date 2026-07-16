"""
app/api/settings.py

Exposes the persistent SettingsManager over HTTP.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.settings import settings_manager, AppSettings

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("")
async def get_settings():
    """Return the current application settings."""
    return settings_manager.settings.model_dump()


@router.post("")
async def update_settings(data: AppSettings):
    """Persist a new settings object."""
    settings_manager.settings = data
    settings_manager.save()
    return settings_manager.settings.model_dump()
