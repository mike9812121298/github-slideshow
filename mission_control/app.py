from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent_runtime import openai_health_status
from db import init_db
from settings import SettingsStore

BASE_DIR = Path(__file__).resolve().parent
UI_DIR = BASE_DIR / "ui"

app = FastAPI(title="Mission Control")
settings_store = SettingsStore(BASE_DIR)


class SettingsUpdate(BaseModel):
    openai_api_key: str | None = Field(default=None)
    openai_model: str | None = Field(default=None)
    whatsapp_phone_number_id: str | None = Field(default=None)
    whatsapp_business_account_id: str | None = Field(default=None)
    whatsapp_webhook_verify_token: str | None = Field(default=None)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/ui")
def ui_index() -> FileResponse:
    return FileResponse(UI_DIR / "index.html")


app.mount("/ui/static", StaticFiles(directory=UI_DIR), name="ui-static")


@app.get("/api/settings")
def get_settings() -> dict:
    return settings_store.get_settings()


@app.post("/api/settings")
def set_settings(payload: SettingsUpdate) -> dict:
    settings_store.set_settings(
        {
            "OPENAI_API_KEY": payload.openai_api_key,
            "OPENAI_MODEL": payload.openai_model,
            "WHATSAPP_PHONE_NUMBER_ID": payload.whatsapp_phone_number_id,
            "WHATSAPP_BUSINESS_ACCOUNT_ID": payload.whatsapp_business_account_id,
            "WHATSAPP_WEBHOOK_VERIFY_TOKEN": payload.whatsapp_webhook_verify_token,
        }
    )
    return settings_store.get_settings()


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "openai": openai_health_status(settings_store),
    }
