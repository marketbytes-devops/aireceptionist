import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ClinicBase(BaseModel):
    name: str = Field(..., example="Sree Kerala Ayurvedic Clinic")
    slug: str = Field(..., example="sree-kerala-ayurveda")
    phone_number: str = Field(..., example="+1234567890")
    address: Optional[str] = Field(None, example="108 Dhanwantari Road, Kochi, Kerala")
    timezone: str = Field("Asia/Kolkata", example="Asia/Kolkata")
    knowledge_base: Optional[str] = None


class ClinicCreate(ClinicBase):
    # Optional initial admin user to create alongside the clinic
    admin_name: Optional[str] = None
    admin_email: Optional[str] = None
    admin_password: Optional[str] = None


class ClinicUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    timezone: Optional[str] = None
    knowledge_base: Optional[str] = None


class ClinicKnowledgeBaseUpdate(BaseModel):
    knowledge_base: str = Field(..., description="Full text guide, doctors, timings, treatments, pricing and FAQs")
    sync_to_elevenlabs: bool = Field(True, description="Whether to automatically push the updated knowledge base to ElevenLabs Agent")


class ClinicResponse(ClinicBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

