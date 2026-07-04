import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.timeline.models import TimelineEvent


async def record_event(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    event_type: str,
    title: str,
    description: Optional[str] = None,
    call_id: Optional[uuid.UUID] = None,
) -> TimelineEvent:
    """
    Single entry point for writing to a patient's health timeline. Other
    domains (calls, and eventually labs/notes/etc.) call this rather than
    inserting TimelineEvent rows directly, so the shape of "what gets
    logged" stays centralized as the product grows.
    """
    event = TimelineEvent(
        patient_id=patient_id,
        call_id=call_id,
        event_type=event_type,
        title=title,
        description=description,
    )
    db.add(event)
    await db.flush()
    return event
