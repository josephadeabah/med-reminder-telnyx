"""
Orchestration for both call flows described in the product spec:

- System -> patient (scheduled): a plain single-leg IVR call. Dispatched
  only by the scheduler (app/scheduler/jobs.py) against due Dose rows -
  there is no "call anyone, anytime" system-call endpoint, by design.
- Caregiver -> patient (on demand): a two-leg bridge. The caregiver's
  phone is dialed first; once they pick up, the patient's phone is dialed
  and the two legs are bridged into a normal live conversation.

Both flows funnel through handle_webhook() below, which is the single
place Telnyx events re-enter the system.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import CallDirection, CallIntent, CallReason, CallStatus, CallType, DoseStatus, TimelineEventType
from app.domains.calls import telnyx_client
from app.domains.calls.intent import classify_intent
from app.domains.calls.models import Call, CallEvent
from app.domains.caregivers.models import Caregiver
from app.domains.medications.models import Dose
from app.domains.patients.models import Patient
from app.domains.timeline import service as timeline_service

MAX_GATHER_RETRIES = 1


class VideoNotSupportedError(Exception):
    """Raised when a video call is requested - see CallType docstring."""


# --------------------------------------------------------------------------
# Loading helpers
# --------------------------------------------------------------------------


async def _load_call(db: AsyncSession, call_id: uuid.UUID) -> Optional[Call]:
    result = await db.execute(
        select(Call)
        .options(
            selectinload(Call.patient),
            selectinload(Call.caregiver),
            selectinload(Call.dose).selectinload(Dose.medication),
        )
        .where(Call.id == call_id)
    )
    return result.scalar_one_or_none()


# --------------------------------------------------------------------------
# System -> patient (scheduled IVR) calls
# --------------------------------------------------------------------------


def _reminder_text(patient_name: str, medication_name: str, dose_text: str) -> str:
    return (
        f"Hello {patient_name}, this is a reminder from your care team to take your {medication_name} "
        f"{dose_text}. Press 1 or say yes if you have taken it. Press 2 or say no if you have not."
    )


def _retry_text() -> str:
    return "Sorry, I didn't catch that. Press 1 or say yes if you've taken your medication. Press 2 or say no if you have not."


def _branch_text(intent: str) -> str:
    if intent == CallIntent.TAKEN.value:
        return "Great, I'll mark that as taken. Thank you, and have a good day."
    if intent == CallIntent.NOT_TAKEN.value:
        return "Thanks, I'll notify your caregiver that this needs attention. Take care."
    return "Sorry, I still didn't catch a clear answer. We'll follow up with you again shortly. Goodbye."


async def trigger_system_call(db: AsyncSession, dose: Dose) -> Call:
    """Places the scheduled medication-check IVR call for one Dose. Called only by the scheduler."""
    patient_result = await db.execute(select(Patient).where(Patient.id == dose.patient_id))
    patient = patient_result.scalar_one()

    call = Call(
        patient_id=patient.id,
        dose_id=dose.id,
        direction=CallDirection.SYSTEM.value,
        call_type=CallType.VOICE.value,
        call_reason=CallReason.MEDICATION_CHECK.value,
        status=CallStatus.QUEUED.value,
    )
    db.add(call)
    await db.flush()

    client_state = telnyx_client.encode_client_state(call.id, "system")
    call.call_control_id = telnyx_client.place_call(to=patient.phone_number, client_state=client_state)
    call.status = CallStatus.INITIATED.value
    await db.commit()
    return call


async def _handle_system_event(db: AsyncSession, call: Call, event_type: str, payload: dict) -> None:
    dose: Optional[Dose] = call.dose

    status_map = {
        "call.initiated": CallStatus.INITIATED.value,
        "call.ringing": CallStatus.RINGING.value,
        "call.answered": CallStatus.ANSWERED.value,
    }
    if event_type in status_map:
        call.status = status_map[event_type]

    if event_type == "call.answered":
        medication_name = dose.medication.name if dose else "your medication"
        dose_text = dose.medication.dose_text if dose else ""
        telnyx_client.gather_using_speak(
            call.call_control_id, text=_reminder_text(call.patient.name, medication_name, dose_text)
        )
        telnyx_client.start_transcription(call.call_control_id)

    elif event_type == "call.transcription":
        transcript = payload.get("transcription_data", {}).get("transcript") or payload.get("transcript") or ""
        if transcript:
            call.transcript = transcript
        if not call.resolved:
            intent = classify_intent(digits=None, speech=transcript)
            if intent in (CallIntent.TAKEN.value, CallIntent.NOT_TAKEN.value):
                await _resolve_system_call(db, call, dose, intent)
                telnyx_client.stop_gather(call.call_control_id)
                telnyx_client.speak(call.call_control_id, text=_branch_text(intent))

    elif event_type == "call.gather.ended":
        if not call.resolved:
            digits = payload.get("digits", "")
            if not digits and call.retry_count < MAX_GATHER_RETRIES:
                call.retry_count += 1
                telnyx_client.gather_using_speak(call.call_control_id, text=_retry_text())
            else:
                intent = classify_intent(digits=digits, speech=call.transcript)
                await _resolve_system_call(db, call, dose, intent)
                telnyx_client.speak(call.call_control_id, text=_branch_text(intent))

    elif event_type == "call.speak.ended" and call.resolved:
        telnyx_client.hangup(call.call_control_id)

    elif event_type == "call.hangup":
        if not call.resolved:
            # Patient never answered, or hung up before giving a clear answer.
            hangup_cause = payload.get("hangup_cause", "")
            call.status = CallStatus.NO_ANSWER.value if hangup_cause != "call_rejected" else CallStatus.BUSY.value
            await _resolve_system_call(db, call, dose, CallIntent.UNKNOWN.value, mark_call_status=False)
        else:
            call.status = CallStatus.COMPLETED.value


async def _resolve_system_call(
    db: AsyncSession, call: Call, dose: Optional[Dose], intent: str, *, mark_call_status: bool = True
) -> None:
    call.intent = intent
    call.resolved = True
    if mark_call_status:
        call.status = CallStatus.COMPLETED.value

    if dose is not None:
        if intent == CallIntent.TAKEN.value:
            dose.status = DoseStatus.CONFIRMED.value
            title, desc = "Medication confirmed", f"{call.patient.name} confirmed taking {dose.medication.name}."
        elif intent == CallIntent.NOT_TAKEN.value:
            dose.status = DoseStatus.MISSED.value
            title, desc = "Medication reported not taken", f"{call.patient.name} reported not taking {dose.medication.name}."
        else:
            dose.status = DoseStatus.ESCALATED.value
            title = "No clear response — escalated"
            desc = f"AI call for {dose.medication.name} got no clear answer. Caregiver should follow up."

        await timeline_service.record_event(
            db,
            patient_id=call.patient_id,
            event_type=TimelineEventType.CALL_SYSTEM.value,
            title=title,
            description=desc,
            call_id=call.id,
        )


# --------------------------------------------------------------------------
# Caregiver -> patient (on-demand bridged) calls
# --------------------------------------------------------------------------


async def trigger_caregiver_call(
    db: AsyncSession,
    *,
    patient: Patient,
    caregiver: Caregiver,
    call_type: str,
    call_reason: Optional[str],
    pre_call_note: Optional[str],
) -> Call:
    if call_type == CallType.VIDEO.value:
        raise VideoNotSupportedError(
            "Video calls require the patient to have the companion app installed and aren't supported by this backend yet."
        )

    call = Call(
        patient_id=patient.id,
        caregiver_id=caregiver.id,
        direction=CallDirection.CAREGIVER.value,
        call_type=CallType.VOICE.value,
        call_reason=call_reason,
        pre_call_note=pre_call_note,
        status=CallStatus.QUEUED.value,
    )
    db.add(call)
    await db.flush()

    client_state = telnyx_client.encode_client_state(call.id, "caregiver")
    call.call_control_id = telnyx_client.place_call(to=caregiver.phone_number, client_state=client_state)
    call.status = CallStatus.INITIATED.value
    await db.commit()
    return call


async def _handle_caregiver_leg_event(db: AsyncSession, call: Call, event_type: str, payload: dict) -> None:
    """Events for the caregiver's own leg (call_control_id)."""
    if event_type == "call.ringing":
        call.status = CallStatus.RINGING.value

    elif event_type == "call.answered":
        call.status = CallStatus.ANSWERED.value
        telnyx_client.speak(call.call_control_id, text="Connecting you now.")
        client_state = telnyx_client.encode_client_state(call.id, "patient")
        call.patient_call_control_id = telnyx_client.place_call(to=call.patient.phone_number, client_state=client_state)

    elif event_type == "call.speak.ended":
        # Only the "sorry, couldn't reach them" message should trigger a
        # hangup here - it's the only speak() issued while status is
        # busy/no-answer. The earlier "Connecting you now" message is
        # spoken while status is "answered", so it's left alone.
        if call.status in (CallStatus.BUSY.value, CallStatus.NO_ANSWER.value) and not call.resolved:
            telnyx_client.hangup(call.call_control_id)

    elif event_type == "call.hangup":
        if call.resolved:
            already_completed = call.status == CallStatus.COMPLETED.value
            call.status = CallStatus.COMPLETED.value
            if call.patient_call_control_id:
                telnyx_client.hangup(call.patient_call_control_id)
            if not already_completed:
                await timeline_service.record_event(
                    db,
                    patient_id=call.patient_id,
                    event_type=TimelineEventType.CALL_CAREGIVER.value,
                    title="Caregiver call ended",
                    description=f"Call between {call.caregiver.name} and {call.patient.name} ended.",
                    call_id=call.id,
                )
        elif call.patient_call_control_id is None:
            # Caregiver's own phone never answered.
            call.status = CallStatus.NO_ANSWER.value
            await timeline_service.record_event(
                db,
                patient_id=call.patient_id,
                event_type=TimelineEventType.CALL_CAREGIVER.value,
                title="Caregiver call — no answer",
                description=f"{call.caregiver.name} didn't answer the call-back.",
                call_id=call.id,
            )


async def _handle_patient_leg_event(db: AsyncSession, call: Call, event_type: str, payload: dict) -> None:
    """Events for the patient's leg (patient_call_control_id) during a caregiver-bridged call."""
    if event_type == "call.answered":
        telnyx_client.bridge(call.patient_call_control_id, other_leg_call_control_id=call.call_control_id)
        call.status = CallStatus.BRIDGED.value
        call.resolved = True
        await timeline_service.record_event(
            db,
            patient_id=call.patient_id,
            event_type=TimelineEventType.CALL_CAREGIVER.value,
            title="Caregiver call connected",
            description=f"{call.caregiver.name} reached {call.patient.name}"
            + (f" — {call.call_reason.replace('_', ' ')}" if call.call_reason else "")
            + (f". Note: {call.pre_call_note}" if call.pre_call_note else "."),
            call_id=call.id,
        )

    elif event_type == "call.hangup":
        if call.resolved:
            already_completed = call.status == CallStatus.COMPLETED.value
            call.status = CallStatus.COMPLETED.value
            telnyx_client.hangup(call.call_control_id)
            if not already_completed:
                await timeline_service.record_event(
                    db,
                    patient_id=call.patient_id,
                    event_type=TimelineEventType.CALL_CAREGIVER.value,
                    title="Caregiver call ended",
                    description=f"Call between {call.caregiver.name} and {call.patient.name} ended.",
                    call_id=call.id,
                )
        else:
            hangup_cause = payload.get("hangup_cause", "")
            call.status = CallStatus.BUSY.value if hangup_cause == "call_rejected" else CallStatus.NO_ANSWER.value
            telnyx_client.speak(call.call_control_id, text=f"Sorry, we couldn't reach {call.patient.name}. Please try again shortly.")
            await timeline_service.record_event(
                db,
                patient_id=call.patient_id,
                event_type=TimelineEventType.CALL_CAREGIVER.value,
                title="Caregiver call — patient unreachable",
                description=f"{call.caregiver.name} tried to reach {call.patient.name}, but there was no answer.",
                call_id=call.id,
            )


# --------------------------------------------------------------------------
# Manual "End call" (AI Call Center live-call banner)
# --------------------------------------------------------------------------


async def end_call(db: AsyncSession, call: Call) -> None:
    if call.call_control_id:
        telnyx_client.hangup(call.call_control_id)
    if call.patient_call_control_id:
        telnyx_client.hangup(call.patient_call_control_id)
    if not call.resolved:
        call.status = CallStatus.COMPLETED.value
        call.resolved = True
    await db.commit()


# --------------------------------------------------------------------------
# Webhook entry point
# --------------------------------------------------------------------------


async def handle_webhook(db: AsyncSession, raw_body: bytes, sig_header: str, timestamp_header: str) -> None:
    event = telnyx_client.verify_and_parse_webhook(raw_body, sig_header, timestamp_header)
    data = event.get("data", {})
    event_type = data.get("event_type", "unknown")
    payload = data.get("payload", {})

    decoded = telnyx_client.decode_client_state(payload.get("client_state"))
    if decoded is None:
        return  # Not one of ours (or malformed state) - acknowledge and ignore.
    call_id, leg = decoded

    call = await _load_call(db, call_id)
    if call is None:
        return

    db.add(CallEvent(call_id=call.id, event_type=event_type, leg=leg, payload=str(payload)))

    if leg == "system":
        await _handle_system_event(db, call, event_type, payload)
    elif leg == "caregiver":
        await _handle_caregiver_leg_event(db, call, event_type, payload)
    elif leg == "patient":
        await _handle_patient_leg_event(db, call, event_type, payload)

    await db.commit()
