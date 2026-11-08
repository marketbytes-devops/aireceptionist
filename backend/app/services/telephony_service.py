import logging
from typing import Optional
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream, Say
from backend.app.core.config import settings
from backend.app.models.clinic import Clinic

logger = logging.getLogger(__name__)


class TelephonyService:
    @staticmethod
    def generate_twiml_media_stream(
        clinic: Clinic,
        host_override: Optional[str] = None
    ) -> str:
        """Generate TwiML response to connect Twilio call to WebSocket Media Stream bridge."""
        response = VoiceResponse()

        # Optional greeting before stream bridge
        greeting = Say(
            f"Namaste and welcome to {clinic.name}. Connecting you to our Ayurvedic voice receptionist.",
            voice="Polly.Aditi",
            language="en-IN"
        )
        response.append(greeting)

        # Base websocket URL
        base_host = host_override or settings.BASE_URL.replace("https://", "").replace("http://", "")
        ws_scheme = "wss" if "https" in settings.BASE_URL else "ws"
        stream_url = f"{ws_scheme}://{base_host}/api/v1/telephony/media-stream/{clinic.id}"

        connect = Connect()
        stream = Stream(url=stream_url)
        # Pass custom parameters to stream
        stream.parameter(name="clinic_id", value=str(clinic.id))
        stream.parameter(name="clinic_name", value=clinic.name)
        connect.append(stream)

        response.append(connect)
        return str(response)

    @staticmethod
    def generate_twiml_elevenlabs_direct(
        clinic: Clinic,
        elevenlabs_phone_number_or_sip: Optional[str] = None
    ) -> str:
        """Generate TwiML redirecting/bridging directly to ElevenLabs Inbound Phone / SIP trunk."""
        response = VoiceResponse()
        target = elevenlabs_phone_number_or_sip or settings.ELEVENLABS_PHONE_NUMBER_ID
        if target:
            response.dial(target)
        else:
            response.say(
                f"Welcome to {clinic.name}. Our AI receptionist is ready to assist you.",
                voice="Polly.Aditi"
            )
        return str(response)

