import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AppointmentOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_name: str
    location: Optional[str]
    scheduled_at: datetime

    model_config = {"from_attributes": True}
