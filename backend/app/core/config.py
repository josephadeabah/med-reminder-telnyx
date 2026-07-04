from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central app configuration, sourced from environment variables (or a
    local .env for the demo). Required vars raise a validation error at
    startup if missing - fail fast rather than fail deep inside a webhook
    or a scheduled job.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    allowed_origins: str = Field(default="http://localhost:3000", alias="ALLOWED_ORIGINS")

    # --- Database ---
    database_url: str = Field(..., alias="DATABASE_URL")

    # --- Telnyx ---
    telnyx_api_key: str = Field(..., alias="TELNYX_API_KEY")
    telnyx_connection_id: str = Field(..., alias="TELNYX_CONNECTION_ID")
    telnyx_public_key: str = Field(..., alias="TELNYX_PUBLIC_KEY")
    telnyx_phone_number: str = Field(..., alias="TELNYX_PHONE_NUMBER")

    # --- Webhooks ---
    public_base_url: str = Field(..., alias="PUBLIC_BASE_URL")
    validate_telnyx_signature: bool = Field(default=True, alias="VALIDATE_TELNYX_SIGNATURE")

    # --- Optional demo protection ---
    demo_admin_token: str = Field(default="", alias="DEMO_ADMIN_TOKEN")

    # --- Scheduler (system-initiated calls at scheduled dose times) ---
    scheduler_enabled: bool = Field(default=True, alias="SCHEDULER_ENABLED")
    dose_dispatch_interval_seconds: int = Field(default=30, alias="DOSE_DISPATCH_INTERVAL_SECONDS")
    dose_due_grace_minutes: int = Field(
        default=2, alias="DOSE_DUE_GRACE_MINUTES", description="How early a dose may be dialed before its scheduled time."
    )

    # --- Demo data ---
    seed_demo_data: bool = Field(default=False, alias="SEED_DEMO_DATA")

    @property
    def async_database_url(self) -> str:
        """Normalizes postgres://... or postgresql://... to the asyncpg driver scheme."""
        url = self.database_url
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        if url.startswith("postgresql://") and "+asyncpg" not in url:
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def webhook_url(self) -> str:
        """Single Telnyx webhook endpoint; events are correlated via client_state."""
        return f"{self.public_base_url.rstrip('/')}/voice/webhook"


@lru_cache
def get_settings() -> Settings:
    return Settings()
