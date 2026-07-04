import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_demo_token
from app.db.session import get_db
from app.domains.timeline.models import TimelineEvent
from app.domains.timeline.schemas import TimelineEventOut

router = APIRouter(prefix="/patients/{patient_id}/timeline", tags=["timeline"], dependencies=[Depends(require_demo_token)])


@router.get("", response_model=list[TimelineEventOut])
async def list_timeline(patient_id: uuid.UUID, limit: int = Query(default=50, le=200), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TimelineEvent)
        .where(TimelineEvent.patient_id == patient_id)
        .order_by(TimelineEvent.occurred_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
