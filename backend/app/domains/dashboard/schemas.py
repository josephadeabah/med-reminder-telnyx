import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ResponseBreakdown(BaseModel):
    confirmed_taken_pct: float
    not_taken_pct: float
    no_answer_pct: float
    skipped_pct: float


class DashboardStats(BaseModel):
    patient_id: uuid.UUID
    period_days: int
    resolved_dose_count: int
    confirmed_pct: float
    missed_or_no_answer_count: int
    upcoming_appointments_count: int
    next_appointment_at: Optional[datetime]
    next_appointment_doctor: Optional[str]
    breakdown: ResponseBreakdown
