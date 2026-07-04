import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_demo_token
from app.db.session import get_db
from app.domains.appointments.models import Appointment
from app.domains.appointments.schemas import AppointmentOut

router = APIRouter(prefix="/patients/{patient_id}/appointments", tags=["appointments"], dependencies=[Depends(require_demo_token)])


@router.get("", response_model=list[AppointmentOut])
async def list_appointments(patient_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Appointment).where(Appointment.patient_id == patient_id).order_by(Appointment.scheduled_at)
    )
    return result.scalars().all()
