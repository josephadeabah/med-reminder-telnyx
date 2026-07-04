"""
Wires the two jobs in jobs.py into an in-process APScheduler instance.

This is the right call for a single-instance deployment (a demo, or a
small production deployment behind one backend replica). If you scale the
backend horizontally, every replica would run its own copy of this
scheduler and could double-dispatch calls - see README "Production
hardening" for the two straightforward ways to fix that (a dedicated
worker process, or an advisory lock keyed on a fixed job name) without
changing anything in jobs.py itself.
"""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import get_settings
from app.scheduler.jobs import dispatch_due_calls_job, ensure_todays_doses_job

logger = logging.getLogger("app.scheduler")

_scheduler: AsyncIOScheduler | None = None


def start_scheduler() -> AsyncIOScheduler | None:
    global _scheduler
    settings = get_settings()
    if not settings.scheduler_enabled:
        logger.info("Scheduler disabled (SCHEDULER_ENABLED=false)")
        return None

    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        ensure_todays_doses_job,
        "cron",
        hour=0,
        minute=0,
        id="ensure_todays_doses",
        misfire_grace_time=3600,
    )
    scheduler.add_job(
        dispatch_due_calls_job,
        "interval",
        seconds=settings.dose_dispatch_interval_seconds,
        id="dispatch_due_calls",
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    _scheduler = scheduler
    logger.info(
        "Scheduler started (dispatch every %ds, dose generation daily at 00:00 UTC)",
        settings.dose_dispatch_interval_seconds,
    )
    return scheduler


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
