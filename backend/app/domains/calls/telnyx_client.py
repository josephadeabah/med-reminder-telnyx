"""
Thin wrapper around the Telnyx Call Control API. Nothing in here knows
about patients, doses, or IVR scripts - it only knows how to place legs,
speak/gather/bridge/hangup them, and (de)serialize the client_state we use
to correlate async webhook events back to a Call row. Business logic that
decides *when* to call these lives in calls/service.py.

Telnyx Call Control is event-driven, not request/response like TwiML: you
place a call, Telnyx posts webhook events to ONE webhook URL as the call
progresses, and you react to each event by issuing one of these actions
back to Telnyx's REST API.
"""

import base64
import json
import uuid

import telnyx

from app.core.config import get_settings

settings = get_settings()
telnyx.api_key = settings.telnyx_api_key


def encode_client_state(call_id: uuid.UUID, leg: str) -> str:
    """`leg` is one of "system", "caregiver", "patient" - see models.Call docstring."""
    return base64.b64encode(json.dumps({"call_id": str(call_id), "leg": leg}).encode()).decode()


def decode_client_state(client_state: str | None) -> tuple[uuid.UUID, str] | None:
    if not client_state:
        return None
    try:
        data = json.loads(base64.b64decode(client_state).decode())
        return uuid.UUID(data["call_id"]), data["leg"]
    except Exception:
        return None


def place_call(*, to: str, client_state: str) -> str:
    """Starts one call leg via Telnyx Call Control. Returns the new leg's call_control_id."""
    call = telnyx.Call.create(
        connection_id=settings.telnyx_connection_id,
        to=to,
        from_=settings.telnyx_phone_number,
        webhook_url=settings.webhook_url,
        webhook_url_method="POST",
        client_state=client_state,
    )
    return call.call_control_id


def gather_using_speak(
    call_control_id: str, *, text: str, valid_digits: str = "12", max_digits: int = 1, timeout_millis: int = 6000
) -> None:
    call = telnyx.Call()
    call.call_control_id = call_control_id
    call.gather_using_speak(
        payload=text,
        voice="female",
        language="en-US",
        valid_digits=valid_digits,
        max=max_digits,
        timeout_millis=timeout_millis,
    )


def start_transcription(call_control_id: str) -> None:
    call = telnyx.Call()
    call.call_control_id = call_control_id
    try:
        call.transcription_start(language="en", transcription_engine="A")
    except Exception:
        # Transcription is a nice-to-have alongside DTMF; never fail the
        # call flow if it can't be started (e.g. feature not enabled yet).
        pass


def stop_gather(call_control_id: str) -> None:
    call = telnyx.Call()
    call.call_control_id = call_control_id
    try:
        call.gather_stop()
    except Exception:
        pass


def speak(call_control_id: str, *, text: str) -> None:
    call = telnyx.Call()
    call.call_control_id = call_control_id
    call.speak(payload=text, voice="female", language="en-US")


def bridge(call_control_id: str, *, other_leg_call_control_id: str) -> None:
    call = telnyx.Call()
    call.call_control_id = call_control_id
    call.bridge(call_control_id=other_leg_call_control_id)


def hangup(call_control_id: str) -> None:
    call = telnyx.Call()
    call.call_control_id = call_control_id
    try:
        call.hangup()
    except Exception:
        # Leg may have already ended (e.g. the other party hung up first) - fine.
        pass


def verify_and_parse_webhook(raw_body: bytes, sig_header: str, timestamp_header: str) -> dict:
    """
    Verifies Telnyx's Ed25519 webhook signature over the exact raw request
    body, then returns the parsed JSON. Raises telnyx.error.SignatureVerificationError
    on a bad signature - callers should turn that into an HTTP 403.
    """
    if settings.validate_telnyx_signature:
        telnyx.Webhook.construct_event(raw_body.decode("utf-8"), sig_header, timestamp_header, settings.telnyx_public_key)
    return json.loads(raw_body)
