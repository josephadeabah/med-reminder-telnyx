import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.domains.calls.models import Call
    from app.domains.patients.models import Patient


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Caregiver(Base):
    """
    A caregiver/family member who can place direct calls to a patient and
    receives escalations. Deliberately minimal for now (no auth fields) -
    see README "Production hardening" for the plan to layer real
    authentication on top without reshaping this table.
    """

    __tablename__ = "caregivers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(32), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)

    patients: Mapped[list["Patient"]] = relationship(back_populates="caregiver")
    calls: Mapped[list["Call"]] = relationship(back_populates="caregiver")
