from fastapi import Header, HTTPException

from app.core.config import get_settings

settings = get_settings()


async def require_demo_token(authorization: str | None = Header(default=None)) -> None:
    """
    Optional bearer-token guard for API routes. No-op when DEMO_ADMIN_TOKEN
    is unset (the default local/demo setup). Set it to lock down a shared
    deployment; the frontend sends it automatically when
    NEXT_PUBLIC_API_TOKEN is configured.

    This is intentionally lightweight - see README "Production hardening"
    for why a real deployment should replace this with proper caregiver
    authentication (e.g. OAuth2/JWT sessions per caregiver) rather than a
    single shared token.
    """
    if not settings.demo_admin_token:
        return

    expected = f"Bearer {settings.demo_admin_token}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
