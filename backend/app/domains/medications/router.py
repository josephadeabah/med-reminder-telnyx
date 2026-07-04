import datetime as dt
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import require_demo_token
from app.db.session import get_db
from app.domains.medications.models import Dose, Medication
from app.domains.medications.schemas import DoseWithCallOut, MedicationOut
from app.domains.medications.service import to_dose_with_call_out

router = APIRouter(prefix="/patients/{patient_id}", tags=["medications"], dependencies=[Depends(require_demo_token)])


@router.get("/medications", response_model=list[MedicationOut])
async def list_medications(patient_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Medication).where(Medication.patient_id == patient_id, Medication.active.is_(True)).order_by(Medication.name)
    )
    return result.scalars().all()


@router.get("/doses", response_model=list[DoseWithCallOut])
async def list_doses(
    patient_id: uuid.UUID,
    on: dt.date | None = Query(default=None, description="Defaults to today (UTC) if omitted"),
    db: AsyncSession = Depends(get_db),
):
    """Powers both the caregiver view's 'Today's medications' and the AI Call Center's 'Today's schedule'."""
    target_date = on or dt.datetime.now(dt.timezone.utc).date()
    start = dt.datetime.combine(target_date, dt.time.min, tzinfo=dt.timezone.utc)
    end = start + dt.timedelta(days=1)

    result = await db.execute(
        select(Dose)
        .options(selectinload(Dose.medication), selectinload(Dose.schedule), selectinload(Dose.calls))
        .where(Dose.patient_id == patient_id, Dose.scheduled_for >= start, Dose.scheduled_for < end)
        .order_by(Dose.scheduled_for)
    )
    doses = result.scalars().all()
    return [to_dose_with_call_out(d) for d in doses]
