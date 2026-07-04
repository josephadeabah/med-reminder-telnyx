import uuid
from datetime import date, datetime, time, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import DoseStatus
from app.db.base import Base

if TYPE_CHECKING:
    from app.domains.calls.models import Call
    from app.domains.patients.models import Patient


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Medication(Base):
    """A prescribed medication for a patient, e.g. 'Metformin 500mg'."""

    __tablename__ = "medications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dose_text: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. "500mg"
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Refill tracking shown in the health snapshot ("Metformin refill: 3 days left")
    refill_due_on: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)

    patient: Mapped["Patient"] = relationship(back_populates="medications")
    schedules: Mapped[list["MedicationSchedule"]] = relationship(
        back_populates="medication", cascade="all, delete-orphan"
    )
    doses: Mapped[list["Dose"]] = relationship(back_populates="medication", cascade="all, delete-orphan")


class MedicationSchedule(Base):
    """
    A recurring daily time this medication should be taken, e.g. 8:00 AM
    ("Morning dose"). `Dose` rows are the concrete daily instances
    generated from these by the scheduler (see app/scheduler/jobs.py).
    """

    __tablename__ = "medication_schedules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )

    time_of_day: Mapped[time] = mapped_column(Time, nullable=False)
    label: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. "Morning dose"
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    medication: Mapped["Medication"] = relationship(back_populates="schedules")
    doses: Mapped[list["Dose"]] = relationship(back_populates="schedule", cascade="all, delete-orphan")


class Dose(Base):
    """
    A single day's concrete instance of a MedicationSchedule - what the
    scheduler actually dials against, and what a system call resolves to
    confirmed/missed/escalated. One row per (schedule, calendar day).
    """

    __tablename__ = "doses"
    __table_args__ = (UniqueConstraint("medication_schedule_id", "scheduled_for", name="uq_dose_schedule_time"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    medication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    medication_schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medication_schedules.id", ondelete="CASCADE"), nullable=False, index=True
    )

    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default=DoseStatus.PENDING.value, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    patient: Mapped["Patient"] = relationship(back_populates="doses")
    medication: Mapped["Medication"] = relationship(back_populates="doses")
    schedule: Mapped["MedicationSchedule"] = relationship(back_populates="doses")
    # A dose could in principle accumulate more than one call attempt over
    # time (e.g. a future re-dial policy); calls.py holds the FK so this
    # stays one-directional. Use `latest_call` for the common case.
    calls: Mapped[list["Call"]] = relationship(back_populates="dose", order_by="Call.created_at")

    @property
    def latest_call(self) -> Optional["Call"]:
        return self.calls[-1] if self.calls else None
