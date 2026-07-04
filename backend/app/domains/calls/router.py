import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import CallStatus
from app.core.security import require_demo_token
from app.db.session import get_db
from app.domains.calls import service
from app.domains.calls.models import Call
from app.domains.calls.schemas import CallOut, CallSummaryOut, CaregiverCallRequest, SystemCallRequest
from app.domains.caregivers.models import Caregiver
from app.domains.medications.models import Dose
from app.domains.patients.models import Patient

logger = logging.getLogger("app.calls")

# Split into two routers: one for the caregiver-facing REST API (auth-gated),
# one for the Telnyx webhook (must stay open to Telnyx, verified by signature instead).
router = APIRouter(prefix="/calls", tags=["calls"], dependencies=[Depends(require_demo_token)])
webhook_router = APIRouter(prefix="/voice", tags=["voice"])

LIVE_STATUSES = [CallStatus.INITIATED.value, CallStatus.RINGING.value, CallStatus.ANSWERED.value, CallStatus.BRIDGED.value]


def _to_summary(call: Call) -> CallSummaryOut:
    return CallSummaryOut(
        id=call.id,
        patient_id=call.patient_id,
        patient_name=call.patient.name,
        caregiver_id=call.caregiver_id,
        dose_id=call.dose_id,
        medication_name=call.dose.medication.name if call.dose else None,
        direction=call.direction,
        call_type=call.call_type,
        call_reason=call.call_reason,
        status=call.status,
        intent=call.intent,
        transcript=call.transcript,
        created_at=call.created_at,
        updated_at=call.updated_at,
    )


@router.post("/caregiver", response_model=CallOut, status_code=201)
async def place_caregiver_call(payload: CaregiverCallRequest, db: AsyncSession = Depends(get_db)):
    """Ticket: 'Direct caregiver-to-patient call' - bridges the caregiver's phone to the patient's phone."""
    patient = await db.get(Patient, payload.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    caregiver = await db.get(Caregiver, payload.caregiver_id)
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")

    try:
        call = await service.trigger_caregiver_call(
            db,
            patient=patient,
            caregiver=caregiver,
            call_type=payload.call_type.value,
            call_reason=payload.call_reason.value if payload.call_reason else None,
            pre_call_note=payload.pre_call_note,
        )
    except service.VideoNotSupportedError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to place caregiver call")
        raise HTTPException(status_code=502, detail=f"Failed to place call via Telnyx: {exc}") from exc

    return await get_call(call.id, db)


@router.post("/system", response_model=CallOut, status_code=201)
async def trigger_system_call_manually(payload: SystemCallRequest, db: AsyncSession = Depends(get_db)):
    """
    Manually (re-)trigger the scheduled medication-check call for a dose -
    mirrors what app/scheduler/jobs.py does automatically. Useful for the
    "Schedule call" action in the AI Call Center UI, and for testing.
    """
    dose = await db.get(Dose, payload.dose_id)
    if not dose:
        raise HTTPException(status_code=404, detail="Dose not found")

    try:
        call = await service.trigger_system_call(db, dose)
    except Exception as exc:
        logger.exception("Failed to place system call")
        raise HTTPException(status_code=502, detail=f"Failed to place call via Telnyx: {exc}") from exc

    return await get_call(call.id, db)


@router.get("", response_model=list[CallSummaryOut])
async def list_calls(
    patient_id: uuid.UUID | None = None,
    direction: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Call)
        .options(selectinload(Call.patient), selectinload(Call.dose).selectinload(Dose.medication))
        .order_by(Call.created_at.desc())
        .limit(min(limit, 200))
    )
    if patient_id:
        stmt = stmt.where(Call.patient_id == patient_id)
    if direction:
        stmt = stmt.where(Call.direction == direction)

    result = await db.execute(stmt)
    return [_to_summary(c) for c in result.scalars().all()]


@router.get("/live", response_model=list[CallSummaryOut])
async def list_live_calls(patient_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db)):
    """Backs the 'Live call in progress' banner in the AI Call Center."""
    stmt = (
        select(Call)
        .options(selectinload(Call.patient), selectinload(Call.dose).selectinload(Dose.medication))
        .where(Call.status.in_(LIVE_STATUSES))
        .order_by(Call.created_at.desc())
    )
    if patient_id:
        stmt = stmt.where(Call.patient_id == patient_id)

    result = await db.execute(stmt)
    return [_to_summary(c) for c in result.scalars().all()]


@router.get("/{call_id}", response_model=CallOut)
async def get_call(call_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Call).options(selectinload(Call.events)).where(Call.id == call_id))
    call = result.scalar_one_or_none()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call


@router.post("/{call_id}/end", response_model=CallOut, status_code=200)
async def end_call(call_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """The 'End call' action in the AI Call Center's live-call banner."""
    call = await db.get(Call, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    await service.end_call(db, call)
    return await get_call(call_id, db)


@webhook_router.post("/webhook")
async def telnyx_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    raw_body = await request.body()
    sig_header = request.headers.get("telnyx-signature-ed25519", "")
    timestamp_header = request.headers.get("telnyx-timestamp", "")

    try:
        await service.handle_webhook(db, raw_body, sig_header, timestamp_header)
    except Exception as exc:
        # Signature failures and similar should read as a clear 403, not a 500.
        if "signature" in str(exc).lower():
            raise HTTPException(status_code=403, detail="Invalid Telnyx webhook signature") from exc
        logger.exception("Error handling Telnyx webhook")
        raise HTTPException(status_code=500, detail="Webhook handling failed") from exc

    return Response(status_code=200)
