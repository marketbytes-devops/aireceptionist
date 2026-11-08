from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ElevenLabsPostCallWebhook(BaseModel):
    call_id: Optional[str] = Field(None, description="ElevenLabs call ID")
    call_sid: Optional[str] = Field(None, description="Twilio Call SID if bridged")
    clinic_id: Optional[str] = Field(None, description="Clinic UUID passed as dynamic variable")
    caller_phone: Optional[str] = Field(None, description="Caller's phone number")
    duration_secs: Optional[int] = Field(None, description="Call duration in seconds")
    recording_url: Optional[str] = Field(None, description="URL of call recording audio")
    transcript: Optional[str] = Field(None, description="Full transcript text or JSON transcript turns")
    summary: Optional[str] = Field(None, description="AI-generated call summary")
    sentiment: Optional[str] = Field(None, description="Sentiment analysis of caller: positive, neutral, negative")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Custom metadata and extracted variables")


class TelephonyStatusResponse(BaseModel):
    status: str
    message: str
    twiml: Optional[str] = None

