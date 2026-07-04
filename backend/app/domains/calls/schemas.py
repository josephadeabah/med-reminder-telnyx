import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.core.enums import CallReason, CallType


class CaregiverCallRequest(BaseModel):
    """Ticket-1 workflow: caregiver places a direct call to their patient."""

    patient_id: uuid.UUID
    caregiver_id: uuid.UUID
    call_type: CallType = CallType.VOICE
    call_reason: Optional[CallReason] = None
    pre_call_note: Optional[str] = Field(default=None, max_length=2000)


class SystemCallRequest(BaseModel):
    """Manually (re-)trigger a scheduled medication-check call for a dose - mirrors what the scheduler does automatically."""

    dose_id: uuid.UUID


class CallEventOut(BaseModel):
    event_type: str
    leg: Optional[str]
    payload: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class CallOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    caregiver_id: Optional[uuid.UUID]
    dose_id: Optional[uuid.UUID]
    direction: str
    call_type: str
    call_reason: Optional[str]
    pre_call_note: Optional[str]
    call_control_id: Optional[str]
    patient_call_control_id: Optional[str]
    status: str
    intent: Optional[str]
    transcript: Optional[str]
    created_at: datetime
    updated_at: datetime
    events: list[CallEventOut] = []

    model_config = {"from_attributes": True}


class CallSummaryOut(BaseModel):
    """Lighter-weight shape for list views (call log, live-call banner) that don't need the full event trace."""

    id: uuid.UUID
    patient_id: uuid.UUID
    patient_name: str
    caregiver_id: Optional[uuid.UUID]
    dose_id: Optional[uuid.UUID]
    medication_name: Optional[str] = None
    direction: str
    call_type: str
    call_reason: Optional[str]
    status: str
    intent: Optional[str]
    transcript: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
