import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class CaregiverOut(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    phone_number: str
    created_at: datetime

    model_config = {"from_attributes": True}
