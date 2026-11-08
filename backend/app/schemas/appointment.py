import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from backend.app.models.appointment import AppointmentStatus


class AppointmentBase(BaseModel):
    clinic_id: uuid.UUID
    doctor_id: uuid.UUID
    patient_name: str = Field(..., example="Rohan Sharma")
    patient_phone: str = Field(..., example="+919876543210")
    patient_email: Optional[str] = Field(None, example="rohan@example.com")
    appointment_time: datetime = Field(..., example="2026-11-10T10:00:00Z")
    treatment_type: Optional[str] = Field("General Ayurvedic Consultation", example="Panchakarma Consultation")
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    appointment_time: Optional[datetime] = None
    doctor_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    call_transcript: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    id: uuid.UUID
    status: AppointmentStatus
    call_transcript: Optional[str] = None
    doctor_name: Optional[str] = None
    clinic_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

