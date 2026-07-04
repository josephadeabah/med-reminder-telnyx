"""
Deterministic yes/no classification for the medication-check IVR script.
Kept as pure functions (no I/O) so this is trivially unit-testable in
isolation from Telnyx or the database.
"""

from app.core.enums import CallIntent

# Negations are checked first: they're more specific and guard against
# substring false-positives (e.g. "have not" must never match a yes-phrase).
_YES_PHRASES = {"yes", "yeah", "yep", "yup", "sure", "correct", "affirmative", "i did", "i took it"}
_NO_PHRASES = {"no", "nope", "not yet", "negative", "haven't", "have not", "didn't", "did not"}


def classify_intent(*, digits: str | None, speech: str | None) -> str:
    digits = (digits or "").strip()
    if digits == "1":
        return CallIntent.TAKEN.value
    if digits == "2":
        return CallIntent.NOT_TAKEN.value

    speech_lower = (speech or "").strip().lower()
    if any(phrase in speech_lower for phrase in _NO_PHRASES):
        return CallIntent.NOT_TAKEN.value
    if any(phrase in speech_lower for phrase in _YES_PHRASES):
        return CallIntent.TAKEN.value

    return CallIntent.UNKNOWN.value
