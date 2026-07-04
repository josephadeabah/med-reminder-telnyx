"""
Shared vocabulary used across domains. Kept as plain Python str Enums
(validated at the Pydantic/API layer) rather than native Postgres ENUM
types, so adding a new value later is a one-line change + migration
instead of an ALTER TYPE dance.
"""

from enum import Enum


class CallDirection(str, Enum):
    SYSTEM = "system"      # AI -> patient, placed automatically at scheduled dose times
    CAREGIVER = "caregiver"  # caregiver -> patient, placed on demand and bridged live


class CallType(str, Enum):
    VOICE = "voice"
    VIDEO = "video"  # accepted for parity with the UI; see calls/service.py for why it's rejected today


class CallReason(str, Enum):
    MEDICATION_CHECK = "medication_check"
    WELLBEING_CHECK = "wellbeing_check"
    APPOINTMENT_REMINDER = "appointment_reminder"
    GENERAL_CHECK = "general_check"
    URGENT_CONCERN = "urgent_concern"


class CallStatus(str, Enum):
    QUEUED = "queued"
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    BRIDGED = "bridged"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no-answer"


class CallIntent(str, Enum):
    TAKEN = "taken"
    NOT_TAKEN = "not_taken"
    UNKNOWN = "unknown"


class DoseStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    MISSED = "missed"
    SKIPPED = "skipped"
    ESCALATED = "escalated"


class TimelineEventType(str, Enum):
    CALL_SYSTEM = "call_system"
    CALL_CAREGIVER = "call_caregiver"
    DOSE = "dose"
    APPOINTMENT = "appointment"
    NOTE = "note"
