import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import CallStatus, CallType
from app.db.base import Base

if TYPE_CHECKING:
    from app.domains.caregivers.models import Caregiver
    from app.domains.medications.models import Dose
    from app.domains.patients.models import Patient
    from app.domains.timeline.models import TimelineEvent


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Call(Base):
    """
    A single phone call, of one of two kinds (see core.enums.CallDirection):

    - "system": the AI dials the patient at a scheduled dose time and runs
      a scripted gather/branch IVR. Only `call_control_id` is used (one leg).
    - "caregiver": a caregiver-initiated call that bridges two live legs -
      the caregiver's phone (`call_control_id`, dialed first) and the
      patient's phone (`patient_call_control_id`, dialed once the
      caregiver answers), connected together once both are up.
    """

    __tablename__ = "calls"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    caregiver_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("caregivers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    dose_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doses.id", ondelete="SET NULL"), nullable=True, index=True
    )

    direction: Mapped[str] = mapped_column(String(16), nullable=False)  # CallDirection
    call_type: Mapped[str] = mapped_column(String(16), default=CallType.VOICE.value, nullable=False)
    call_reason: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # CallReason
    pre_call_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    call_control_id: Mapped[Optional[str]] = mapped_column(String(128), unique=True, index=True, nullable=True)
    patient_call_control_id: Mapped[Optional[str]] = mapped_column(String(128), unique=True, index=True, nullable=True)

    status: Mapped[str] = mapped_column(String(32), default=CallStatus.QUEUED.value, nullable=False)
    intent: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # CallIntent, system calls only
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    patient: Mapped["Patient"] = relationship(back_populates="calls")
    caregiver: Mapped[Optional["Caregiver"]] = relationship(back_populates="calls")
    dose: Mapped[Optional["Dose"]] = relationship(back_populates="calls")
    events: Mapped[list["CallEvent"]] = relationship(
        back_populates="call", cascade="all, delete-orphan", order_by="CallEvent.created_at"
    )
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(back_populates="call")


class CallEvent(Base):
    """Audit trail of every Telnyx webhook event received for a call leg."""

    __tablename__ = "call_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("calls.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    leg: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # "caregiver" | "patient" | "system"
    payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)

    call: Mapped["Call"] = relationship(back_populates="events")
