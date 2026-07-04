import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class PatientOut(BaseModel):
    id: uuid.UUID
    name: str
    date_of_birth: Optional[date]
    age: Optional[int]
    relation_to_caregiver: Optional[str]
    phone_number: str
    phone_label: str
    ai_monitoring_enabled: bool
    last_hba1c: Optional[float]
    last_hba1c_at: Optional[date]
    primary_caregiver_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HealthSnapshot(BaseModel):
    """Backs the caregiver-view sidebar: adherence, next appointment, labs, refills."""

    adherence_30day_pct: Optional[float]
    next_appointment_at: Optional[datetime]
    next_appointment_doctor: Optional[str]
    last_hba1c: Optional[float]
    last_hba1c_at: Optional[date]
    next_refill_medication: Optional[str]
    next_refill_days_remaining: Optional[int]
