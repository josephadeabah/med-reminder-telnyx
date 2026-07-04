import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.domains.calls.models import Call
    from app.domains.patients.models import Patient


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimelineEvent(Base):
    """
    The patient's health timeline. Calls (both system and caregiver) are
    logged here automatically on resolution - this is the backing store
    for "Calls are logged automatically to Robert's health timeline" in
    the caregiver UI. Designed to hold other event kinds too (dose,
    appointment, note) as the product grows.
    """

    __tablename__ = "timeline_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    call_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("calls.id", ondelete="SET NULL"), nullable=True
    )

    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)

    patient: Mapped["Patient"] = relationship(back_populates="timeline_events")
    call: Mapped[Optional["Call"]] = relationship(back_populates="timeline_events")
