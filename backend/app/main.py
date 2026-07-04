import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import get_settings
from app.db import models_registry  # noqa: F401  (registers every domain's models before any query runs)
from app.db.session import engine
from app.domains.appointments.router import router as appointments_router
from app.domains.calls.router import router as calls_router
from app.domains.calls.router import webhook_router
from app.domains.caregivers.router import router as caregivers_router
from app.domains.dashboard.router import router as dashboard_router
from app.domains.medications.router import router as medications_router
from app.domains.patients.router import router as patients_router
from app.domains.timeline.router import router as timeline_router
from app.scheduler.runner import shutdown_scheduler, start_scheduler

settings = get_settings()

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Medication Reminder API (Telnyx) - env=%s", settings.app_env)

    # Schema is owned by Alembic migrations (see backend/alembic), not
    # auto-created here. We just verify connectivity so a misconfigured
    # DATABASE_URL fails loudly at boot instead of on the first request.
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection OK")
    except Exception:
        logger.exception("Database connectivity check failed at startup")
        raise

    start_scheduler()
    yield
    shutdown_scheduler()
    logger.info("Shutting down")


app = FastAPI(
    title="Medication Reminder Call API (Telnyx)",
    description=(
        "System-to-patient scheduled medication reminder calls and on-demand "
        "caregiver-to-patient bridged calls, both via Telnyx Call Control."
    ),
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Domain routers - see app/domains/*/router.py. Add new domains' routers
# here as the product grows; each domain owns its own URL prefix.
app.include_router(patients_router)
app.include_router(caregivers_router)
app.include_router(medications_router)
app.include_router(appointments_router)
app.include_router(timeline_router)
app.include_router(calls_router)
app.include_router(webhook_router)
app.include_router(dashboard_router)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "env": settings.app_env}


@app.get("/", tags=["meta"])
async def root():
    return {"message": "Medication Reminder Call API (Telnyx)", "docs": "/docs", "health": "/health"}
