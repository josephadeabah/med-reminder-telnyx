from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_demo_token
from app.db.session import get_db
from app.domains.caregivers.models import Caregiver
from app.domains.caregivers.schemas import CaregiverOut

router = APIRouter(prefix="/caregivers", tags=["caregivers"], dependencies=[Depends(require_demo_token)])


@router.get("", response_model=list[CaregiverOut])
async def list_caregivers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Caregiver).order_by(Caregiver.name))
    return result.scalars().all()


@router.get("/me", response_model=CaregiverOut)
async def get_current_caregiver(db: AsyncSession = Depends(get_db)):
    """
    Stand-in for real session-based auth: returns the first seeded
    caregiver. Swap this for `Depends(get_authenticated_caregiver)` once
    proper login is wired up - every call site that needs "the current
    caregiver" already goes through this one function.
    """
    result = await db.execute(select(Caregiver).order_by(Caregiver.created_at).limit(1))
    caregiver = result.scalar_one_or_none()
    if not caregiver:
        raise HTTPException(status_code=404, detail="No caregiver has been seeded yet")
    return caregiver
