import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.dashboard.service import get_dashboard_stats
from app.domains.medications.models import Medication
from app.domains.patients.schemas import HealthSnapshot


async def get_health_snapshot(db: AsyncSession, *, patient_id: uuid.UUID) -> HealthSnapshot:
    """Backs the caregiver-view sidebar: adherence, next appointment, labs, refills."""
    stats = await get_dashboard_stats(db, patient_id=patient_id, days=30)

    from app.domains.patients.models import Patient  # local import avoids a module-level cross-domain cycle

    patient = await db.get(Patient, patient_id)

    med_result = await db.execute(
        select(Medication)
        .where(Medication.patient_id == patient_id, Medication.active.is_(True), Medication.refill_due_on.is_not(None))
        .order_by(Medication.refill_due_on)
        .limit(1)
    )
    next_refill_med = med_result.scalar_one_or_none()
    refill_days_remaining = None
    if next_refill_med and next_refill_med.refill_due_on:
        refill_days_remaining = (next_refill_med.refill_due_on - datetime.now(timezone.utc).date()).days

    return HealthSnapshot(
        adherence_30day_pct=stats.confirmed_pct if stats.resolved_dose_count else None,
        next_appointment_at=stats.next_appointment_at,
        next_appointment_doctor=stats.next_appointment_doctor,
        last_hba1c=float(patient.last_hba1c) if patient and patient.last_hba1c is not None else None,
        last_hba1c_at=patient.last_hba1c_at if patient else None,
        next_refill_medication=next_refill_med.name if next_refill_med else None,
        next_refill_days_remaining=refill_days_remaining,
    )
