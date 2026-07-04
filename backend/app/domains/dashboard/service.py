"""
Adherence/response aggregation, shared by the AI Call Center dashboard and
the caregiver-view health snapshot. Kept as one function so both surfaces
can never drift into computing "confirmed %" two different ways.
"""

import datetime as dt
import uuid
from collections import Counter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import DoseStatus
from app.domains.appointments.models import Appointment
from app.domains.dashboard.schemas import DashboardStats, ResponseBreakdown
from app.domains.medications.models import Dose

RESOLVED_STATUSES = {
    DoseStatus.CONFIRMED.value,
    DoseStatus.MISSED.value,
    DoseStatus.ESCALATED.value,
    DoseStatus.SKIPPED.value,
}


async def get_dashboard_stats(db: AsyncSession, *, patient_id: uuid.UUID, days: int = 30) -> DashboardStats:
    now = dt.datetime.now(dt.timezone.utc)
    since = now - dt.timedelta(days=days)

    dose_result = await db.execute(
        select(Dose.status).where(Dose.patient_id == patient_id, Dose.scheduled_for >= since, Dose.scheduled_for <= now)
    )
    counts = Counter(row[0] for row in dose_result.all())
    resolved_total = sum(counts[s] for s in RESOLVED_STATUSES)

    def pct(status: str) -> float:
        return round((counts[status] / resolved_total) * 100, 1) if resolved_total else 0.0

    appt_result = await db.execute(
        select(Appointment)
        .where(Appointment.patient_id == patient_id, Appointment.scheduled_at >= now)
        .order_by(Appointment.scheduled_at)
    )
    upcoming_appointments = appt_result.scalars().all()
    next_appointment = upcoming_appointments[0] if upcoming_appointments else None

    return DashboardStats(
        patient_id=patient_id,
        period_days=days,
        resolved_dose_count=resolved_total,
        confirmed_pct=pct(DoseStatus.CONFIRMED.value),
        missed_or_no_answer_count=counts[DoseStatus.MISSED.value] + counts[DoseStatus.ESCALATED.value],
        upcoming_appointments_count=len(upcoming_appointments),
        next_appointment_at=next_appointment.scheduled_at if next_appointment else None,
        next_appointment_doctor=next_appointment.doctor_name if next_appointment else None,
        breakdown=ResponseBreakdown(
            confirmed_taken_pct=pct(DoseStatus.CONFIRMED.value),
            not_taken_pct=pct(DoseStatus.MISSED.value),
            no_answer_pct=pct(DoseStatus.ESCALATED.value),
            skipped_pct=pct(DoseStatus.SKIPPED.value),
        ),
    )
