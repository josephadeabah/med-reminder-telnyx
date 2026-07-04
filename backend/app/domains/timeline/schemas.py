import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TimelineEventOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    call_id: Optional[uuid.UUID]
    event_type: str
    title: str
    description: Optional[str]
    occurred_at: datetime

    model_config = {"from_attributes": True}
