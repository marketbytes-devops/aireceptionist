import json
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, Request, Response, WebSocket, WebSocketDisconnect, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import websockets
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.elevenlabs_config import (
    build_conversation_initiation_payload,
    get_ist_time_greeting,
)
from backend.app.services.elevenlabs_pool import (
    get_active_agent_credentials,
    get_pool_status,
)
from backend.app.models.clinic import Clinic
from backend.app.models.call_log import CallLog
from backend.app.services.telephony_service import TelephonyService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telephony", tags=["Twilio & Telephony Bridge"])


@router.post("/incoming-call")
async def incoming_twilio_call(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Twilio Voice Webhook: handles incoming phone calls to any clinic's Twilio phone number.
    Returns TwiML that connects the call audio to the WebSocket Media Stream bridge.
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "")
    caller_phone = form_data.get("From", "")
    called_phone = form_data.get("To", "")

    logger.info(f"Incoming call: CallSid={call_sid}, From={caller_phone}, To={called_phone}")

    # Look up clinic by Twilio called number
    clinic = None
    if called_phone:
        stmt = select(Clinic).where(Clinic.phone_number == called_phone)
        res = await db.execute(stmt)
        clinic = res.scalar_one_or_none()

    # If not matched by exact phone, fallback to first clinic
    if not clinic:
        first_stmt = select(Clinic).limit(1)
        res = await db.execute(first_stmt)
        clinic = res.scalar_one_or_none()

    if not clinic:
        # Fallback dummy clinic if none registered yet
        clinic = Clinic(
            id=uuid.uuid4(),
            name="AyurVoice Ayurvedic Center",
            slug="ayurvoice-default",
            phone_number=called_phone or "+1000000000",
            address="Kerala, India"
        )

    # Initialize a CallLog record for tracking
    try:
        new_call_log = CallLog(
            clinic_id=clinic.id,
            call_sid=call_sid,
            caller_phone=caller_phone or "Unknown",
            outcome="in_progress"
        )
        db.add(new_call_log)
        await db.commit()
    except Exception as e:
        logger.warning(f"Could not initialize call log: {e}")

    # Extract host header for dynamic ngrok / production URL compatibility
    host = request.headers.get("host") or settings.BASE_URL.replace("https://", "").replace("http://", "")
    twiml_content = TelephonyService.generate_twiml_media_stream(clinic, host_override=host)

    return Response(content=twiml_content, media_type="application/xml")


@router.get("/active-agent")
async def get_active_telephony_agent():
    """Return the currently active ElevenLabs agent configuration (Primary vs Backup failover)
    along with dynamic IST greeting variables for the frontend simulator.
    """
    creds = await get_active_agent_credentials()
    dynamic_vars = get_ist_time_greeting()
    return {
        "account": creds.get("account"),
        "agent_id": creds.get("agent_id"),
        "is_backup": creds.get("is_backup", False),
        "remaining_credits": creds.get("remaining", 0),
        "character_count": creds.get("character_count", 0),
        "character_limit": creds.get("character_limit", 10000),
        "threshold": creds.get("threshold", 300),
        "dynamic_variables": dynamic_vars,
    }


@router.get("/pool-status")
async def get_elevenlabs_pool_status():
    """Return credit and health status for both Primary and Backup ElevenLabs accounts."""
    return await get_pool_status()


@router.websocket("/media-stream/{clinic_id}")
async def twilio_media_stream_websocket(
    websocket: WebSocket,
    clinic_id: uuid.UUID
):
    """WebSocket endpoint connecting Twilio Media Stream with ElevenLabs Conversational AI Realtime API.
    
    Streams bidirectional mulaw/PCM audio:
    Twilio Call -> WebSocket Media Stream -> ElevenLabs Conversational AI Agent (with Auto-Failover)
    """
    await websocket.accept()
    logger.info(f"Twilio Media Stream WebSocket connected for clinic: {clinic_id}")

    stream_sid = None
    call_sid = None
    elevenlabs_ws = None

    creds = await get_active_agent_credentials()
    active_agent_id = creds.get("agent_id")
    active_api_key = creds.get("api_key")

    elevenlabs_url = (
        f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={active_agent_id}"
    )

    try:
        # Connect to ElevenLabs Conversational AI WebSocket if API key / agent configured
        if active_api_key and active_agent_id:
            elevenlabs_ws = await websockets.connect(
                elevenlabs_url,
                extra_headers={"xi-api-key": active_api_key}
            )
            await elevenlabs_ws.send(json.dumps(build_conversation_initiation_payload()))
            logger.info(
                f"Connected to ElevenLabs Realtime WebSocket agent "
                f"({creds.get('account')}: {active_agent_id}) with IST greeting data."
            )

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            event = message.get("event")

            if event == "start":
                stream_sid = message["start"]["streamSid"]
                call_sid = message["start"]["callSid"]
                logger.info(f"Media stream started: StreamSid={stream_sid}, CallSid={call_sid}")

            elif event == "media":
                # Audio payload in base64 (mulaw 8000Hz from Twilio)
                payload = message["media"]["payload"]
                if elevenlabs_ws and not elevenlabs_ws.closed:
                    # Forward user audio chunk to ElevenLabs
                    await elevenlabs_ws.send(json.dumps({
                        "user_audio_chunk": payload
                    }))

            elif event == "stop":
                logger.info(f"Media stream stopped for StreamSid={stream_sid}")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for clinic {clinic_id}")
    except Exception as e:
        logger.error(f"Error in media stream bridge: {e}")
    finally:
        if elevenlabs_ws and not elevenlabs_ws.closed:
            await elevenlabs_ws.close()
        logger.info("Media stream bridge session closed.")

