"""
Business logic for medications/schedules/doses - kept separate from the
router so the scheduler (app/scheduler/jobs.py) can reuse the same
dose-generation logic without importing HTTP concerns.
"""

import datetime as dt
import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.medications.models import Dose, MedicationSchedule
from app.domains.medications.schemas import DoseWithCallOut


async def ensure_doses_for_date(db: AsyncSession, *, target_date: dt.date) -> int:
    """
    Idempotently creates one Dose row per active MedicationSchedule for
    `target_date`. Safe to call repeatedly (e.g. every scheduler tick, or
    once at midnight) - relies on the DB-level unique constraint on
    (medication_schedule_id, scheduled_for) to skip rows that already
    exist rather than needing a SELECT-then-INSERT race window.
    """
    result = await db.execute(select(MedicationSchedule).where(MedicationSchedule.active.is_(True)))
    schedules = result.scalars().all()

    created = 0
    for schedule in schedules:
        scheduled_for = dt.datetime.combine(target_date, schedule.time_of_day, tzinfo=dt.timezone.utc)
        stmt = (
            pg_insert(Dose)
            .values(
                id=uuid.uuid4(),
                patient_id=schedule.patient_id,
                medication_id=schedule.medication_id,
                medication_schedule_id=schedule.id,
                scheduled_for=scheduled_for,
            )
            .on_conflict_do_nothing(constraint="uq_dose_schedule_time")
        )
        res = await db.execute(stmt)
        created += res.rowcount or 0

    await db.commit()
    return created


def to_dose_with_call_out(dose: Dose) -> DoseWithCallOut:
    latest_call = dose.latest_call
    return DoseWithCallOut(
        id=dose.id,
        patient_id=dose.patient_id,
        medication_id=dose.medication_id,
        medication_name=dose.medication.name,
        medication_dose_text=dose.medication.dose_text,
        schedule_label=dose.schedule.label,
        scheduled_for=dose.scheduled_for,
        status=dose.status,
        call_id=latest_call.id if latest_call else None,
        call_status=latest_call.status if latest_call else None,
        call_intent=latest_call.intent if latest_call else None,
        call_transcript=latest_call.transcript if latest_call else None,
    )
