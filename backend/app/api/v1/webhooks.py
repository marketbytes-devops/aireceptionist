import json
import uuid
import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.call_log import CallLog
from backend.app.models.appointment import Appointment
from backend.app.schemas.telephony import ElevenLabsPostCallWebhook

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Post-Call Analytics Webhooks"])


@router.post("/elevenlabs-post-call")
async def elevenlabs_post_call_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """ElevenLabs Post-Call Webhook: Receives call duration, audio recording URL, and full transcript.
    Updates the respective appointment and call log in the database.
    """
    body_bytes = await request.body()
    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        payload = {}

    logger.info(f"Received ElevenLabs Post-Call Webhook payload: {payload}")

    # Extract ElevenLabs standard post-call fields
    call_id = payload.get("call_id") or payload.get("id")
    call_sid = payload.get("call_sid") or payload.get("custom_parameters", {}).get("call_sid")
    duration_secs = payload.get("duration_secs") or payload.get("call_duration_secs")
    recording_url = payload.get("recording_url") or payload.get("audio_url")
    
    # Transcript can be a string or list of dialogue turns: [{"role": "agent", "message": "..."}, ...]
    raw_transcript = payload.get("transcript")
    if isinstance(raw_transcript, list):
        transcript_text = "\n".join(
            f"{turn.get('role', 'Speaker').capitalize()}: {turn.get('message', '')}"
            for turn in raw_transcript
        )
    elif isinstance(raw_transcript, str):
        transcript_text = raw_transcript
    else:
        transcript_text = None

    summary = payload.get("analysis", {}).get("transcript_summary") or payload.get("summary")
    sentiment = payload.get("analysis", {}).get("sentiment") or payload.get("sentiment")
    caller_phone = payload.get("from_number") or payload.get("caller_phone") or "Unknown"

    clinic_id_str = (
        payload.get("custom_parameters", {}).get("clinic_id") or
        payload.get("clinic_id")
    )
    clinic_id = None
    if clinic_id_str:
        try:
            clinic_id = uuid.UUID(clinic_id_str)
        except ValueError:
            pass

    # Try to find existing CallLog by call_sid or call_id
    call_log = None
    if call_sid:
        stmt = select(CallLog).where(CallLog.call_sid == call_sid).order_by(CallLog.created_at.desc())
        res = await db.execute(stmt)
        call_log = res.scalars().first()

    if not call_log and clinic_id:
        # Create new CallLog
        call_log = CallLog(
            clinic_id=clinic_id,
            call_sid=call_sid or call_id,
            caller_phone=caller_phone
        )
        db.add(call_log)

    if call_log:
        if duration_secs:
            call_log.duration_seconds = int(duration_secs)
        if recording_url:
            call_log.recording_url = recording_url
        if transcript_text:
            call_log.transcript = transcript_text
        if summary:
            call_log.summary = summary
        if sentiment:
            call_log.sentiment = str(sentiment)
        call_log.outcome = "completed"

    # Also match with most recent Appointment for this caller phone if applicable
    if caller_phone and caller_phone != "Unknown":
        clean_phone = caller_phone.replace("+", "").replace("-", "").strip()
        app_stmt = (
            select(Appointment)
            .where(Appointment.patient_phone.ilike(f"%{clean_phone[-10:]}%"))
            .order_by(Appointment.created_at.desc())
        )
        app_res = await db.execute(app_stmt)
        matched_appointment = app_res.scalars().first()
        if matched_appointment and transcript_text:
            matched_appointment.call_transcript = transcript_text
            if call_log:
                call_log.appointment_id = matched_appointment.id

    await db.commit()
    logger.info("Successfully processed ElevenLabs post-call webhook and updated database.")
    return {"status": "success", "message": "Call log and transcript updated successfully."}

