from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

from db import get_connection


@dataclass
class SettingsStore:
    root_path: Path = Path(__file__).resolve().parent

    def __post_init__(self) -> None:
        self.env_path = self.root_path / ".env"
        self.defaults: dict[str, str] = {
            "OPENAI_MODEL": "gpt-4o-mini",
            "PORT": "8080",
            "WHATSAPP_PHONE_NUMBER_ID": "",
            "WHATSAPP_BUSINESS_ACCOUNT_ID": "",
            "WHATSAPP_WEBHOOK_VERIFY_TOKEN": "",
        }

    def _load_env_settings(self) -> dict[str, str]:
        env_values = dotenv_values(self.env_path)
        return {k: str(v) for k, v in env_values.items() if v is not None}

    def _load_db_settings(self) -> dict[str, str]:
        with get_connection() as conn:
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
        return {row["key"]: row["value"] for row in rows if row["value"] is not None}

    def _resolve_settings(self) -> dict[str, str]:
        resolved = dict(self.defaults)
        resolved.update(self._load_env_settings())
        resolved.update(self._load_db_settings())
        return resolved

    @staticmethod
    def _masked_key(key: str) -> str:
        if not key:
            return ""
        if len(key) <= 8:
            return "*" * len(key)
        return f"{key[:4]}{'*' * (len(key) - 8)}{key[-4:]}"

    def get_openai_key(self) -> str:
        return self._resolve_settings().get("OPENAI_API_KEY", "")

    def get_settings(self) -> dict[str, Any]:
        resolved = self._resolve_settings()
        key = resolved.get("OPENAI_API_KEY", "")
        return {
            "openai_api_key_set": bool(key),
            "openai_api_key_masked": self._masked_key(key),
            "openai_model": resolved.get("OPENAI_MODEL", self.defaults["OPENAI_MODEL"]),
            "port": int(resolved.get("PORT", self.defaults["PORT"])),
            "whatsapp": {
                "phone_number_id": resolved.get("WHATSAPP_PHONE_NUMBER_ID", ""),
                "business_account_id": resolved.get("WHATSAPP_BUSINESS_ACCOUNT_ID", ""),
                "webhook_verify_token_set": bool(
                    resolved.get("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "")
                ),
            },
        }

    def set_settings(self, values: dict[str, str]) -> None:
        allowed_keys = {
            "OPENAI_API_KEY",
            "OPENAI_MODEL",
            "WHATSAPP_PHONE_NUMBER_ID",
            "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "WHATSAPP_WEBHOOK_VERIFY_TOKEN",
        }
        updates = {k: v for k, v in values.items() if k in allowed_keys and v is not None}
        if not updates:
            return

        with get_connection() as conn:
            for key, value in updates.items():
                conn.execute(
                    """
                    INSERT INTO settings (key, value)
                    VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value
                    """,
                    (key, value),
                )
            conn.commit()
