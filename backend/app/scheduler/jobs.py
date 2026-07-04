"""
The two background jobs that make "system calls happen automatically at
scheduled dose times" (as opposed to "someone has to click a button") real:

1. ensure_todays_doses_job - materializes today's Dose rows from each
   patient's MedicationSchedule. Runs once at startup and once a day.
2. dispatch_due_calls_job - finds doses that are due and haven't been
   called yet, and places the system IVR call for each. Runs frequently
   (DOSE_DISPATCH_INTERVAL_SECONDS).

Both are plain async functions with no APScheduler-specific code, so
they're easy to unit test or move to a different scheduler later.
"""

import datetime as dt
import logging

from sqlalchemy import exists, select
from sqlalchemy.orm import selectinload

from app.core.enums import DoseStatus
from app.db import models_registry  # noqa: F401  (registers every domain's models before any query runs)
from app.db.session import AsyncSessionLocal
from app.domains.calls.models import Call
from app.domains.calls.service import trigger_system_call
from app.domains.medications.models import Dose
from app.domains.medications.service import ensure_doses_for_date

logger = logging.getLogger("app.scheduler")


async def ensure_todays_doses_job() -> None:
    async with AsyncSessionLocal() as db:
        today = dt.datetime.now(dt.timezone.utc).date()
        created = await ensure_doses_for_date(db, target_date=today)
        if created:
            logger.info("Generated %d dose(s) for %s", created, today)


async def dispatch_due_calls_job() -> None:
    """
    Dispatches exactly one system call per due dose. A dose counts as
    "already dispatched" the moment a Call row exists for it - not when
    Dose.status changes, since status stays "pending" for the whole
    duration the call is ringing/in-progress. Checking Dose.status alone
    here would re-dial the same dose on every tick until it resolves.
    """
    now = dt.datetime.now(dt.timezone.utc)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Dose)
            .options(selectinload(Dose.patient), selectinload(Dose.medication))
            .where(
                Dose.status == DoseStatus.PENDING.value,
                Dose.scheduled_for <= now,
                ~exists().where(Call.dose_id == Dose.id),
            )
            .with_for_update(skip_locked=True)
        )
        due_doses = result.scalars().all()

        for dose in due_doses:
            if not dose.patient.ai_monitoring_enabled:
                continue
            try:
                await trigger_system_call(db, dose)
                logger.info("Dispatched system call for dose %s (%s)", dose.id, dose.medication.name)
            except Exception:
                logger.exception("Failed to dispatch system call for dose %s", dose.id)
