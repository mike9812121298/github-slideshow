from __future__ import annotations

from settings import SettingsStore


def openai_health_status(settings_store: SettingsStore) -> dict[str, str | bool]:
    key = settings_store.get_openai_key().strip()
    settings = settings_store.get_settings()
    return {
        "openai_configured": bool(key),
        "openai_model": settings["openai_model"],
        "status": "configured" if key else "missing_api_key",
    }
