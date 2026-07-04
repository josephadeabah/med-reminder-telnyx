import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_demo_token
from app.db.session import get_db
from app.domains.patients import service
from app.domains.patients.models import Patient
from app.domains.patients.schemas import HealthSnapshot, PatientOut

router = APIRouter(prefix="/patients", tags=["patients"], dependencies=[Depends(require_demo_token)])


@router.get("", response_model=list[PatientOut])
async def list_patients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).order_by(Patient.name))
    return result.scalars().all()


@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(patient_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/{patient_id}/snapshot", response_model=HealthSnapshot)
async def get_snapshot(patient_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    if not await db.get(Patient, patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    return await service.get_health_snapshot(db, patient_id=patient_id)
