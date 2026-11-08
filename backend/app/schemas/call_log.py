import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CallLogBase(BaseModel):
    clinic_id: uuid.UUID
    call_sid: Optional[str] = Field(None, example="CA1234567890abcdef")
    caller_phone: str = Field(..., example="+919876543210")
    duration_seconds: Optional[int] = Field(None, example=145)
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = Field(None, example="positive")
    outcome: Optional[str] = Field(None, example="appointment_booked")
    appointment_id: Optional[uuid.UUID] = None


class CallLogCreate(CallLogBase):
    pass


class CallLogResponse(CallLogBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

