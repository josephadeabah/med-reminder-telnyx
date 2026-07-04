import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.domains.appointments.models import Appointment
    from app.domains.calls.models import Call
    from app.domains.caregivers.models import Caregiver
    from app.domains.medications.models import Dose, Medication
    from app.domains.timeline.models import TimelineEvent


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Denormalized on Patient for now since this POC models one primary
    # caregiver per patient. A future multi-caregiver model would move
    # this onto a caregiver_patient_links table instead - see README.
    relation_to_caregiver: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # e.g. "Your father"
    primary_caregiver_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("caregivers.id", ondelete="SET NULL"), nullable=True
    )

    phone_number: Mapped[str] = mapped_column(String(32), nullable=False)
    phone_label: Mapped[str] = mapped_column(String(64), default="Primary · Mobile", nullable=False)

    ai_monitoring_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Health snapshot fields shown in the caregiver UI sidebar
    last_hba1c: Mapped[Optional[float]] = mapped_column(Numeric(4, 1), nullable=True)
    last_hba1c_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    caregiver: Mapped[Optional["Caregiver"]] = relationship(back_populates="patients")
    medications: Mapped[list["Medication"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    doses: Mapped[list["Dose"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    calls: Mapped[list["Call"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )

    @property
    def age(self) -> Optional[int]:
        if not self.date_of_birth:
            return None
        today = date.today()
        years = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            years -= 1
        return years
