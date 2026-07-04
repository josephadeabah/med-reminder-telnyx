import uuid
from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel


class MedicationOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    name: str
    dose_text: str
    active: bool
    refill_due_on: Optional[date]

    model_config = {"from_attributes": True}


class MedicationScheduleOut(BaseModel):
    id: uuid.UUID
    medication_id: uuid.UUID
    time_of_day: time
    label: str
    active: bool

    model_config = {"from_attributes": True}


class DoseOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    medication_id: uuid.UUID
    medication_name: str
    medication_dose_text: str
    schedule_label: str
    scheduled_for: datetime
    status: str

    model_config = {"from_attributes": True}


class DoseWithCallOut(DoseOut):
    """Today's-schedule view: includes the resolved call's response/duration, if any."""

    call_id: Optional[uuid.UUID] = None
    call_status: Optional[str] = None
    call_intent: Optional[str] = None
    call_transcript: Optional[str] = None
