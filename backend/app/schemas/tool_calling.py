import uuid
from typing import Optional, List
from pydantic import BaseModel, Field


class CheckAvailabilityRequest(BaseModel):
    clinic_id: Optional[uuid.UUID] = Field(None, description="Unique ID of the clinic (optional, defaults to primary clinic)")
    doctor_name: Optional[str] = Field(None, description="Doctor name requested by the patient, e.g. 'Dr. Varma'")
    date_time: str = Field(..., description="Requested date or ISO datetime, e.g. '2026-11-10' or '2026-11-10T10:00:00'")
    treatment_type: Optional[str] = Field(None, description="Ayurvedic treatment or consultation type")


class CheckAvailabilityResponse(BaseModel):
    available: bool = Field(..., description="Whether slots are available")
    message: str = Field(..., description="Natural language response synthesized for the voice agent")
    available_slots: List[str] = Field(default=[], description="List of available ISO timestamp strings")
    doctor_id: Optional[uuid.UUID] = None
    doctor_name: Optional[str] = None
    consultation_fee: Optional[float] = None


class BookAppointmentRequest(BaseModel):
    clinic_id: Optional[uuid.UUID] = Field(None, description="Unique ID of the clinic (optional, defaults to primary clinic)")
    doctor_name: Optional[str] = Field(None, description="Optional doctor name; defaults to clinic's available doctor")
    patient_name: str = Field(..., description="Full name of the patient")
    patient_phone: str = Field(..., description="Patient contact phone number with country code")
    patient_email: Optional[str] = Field(None, description="Optional patient email for notifications")
    appointment_time: str = Field(..., description="Confirmed ISO datetime string for the booking")
    treatment_type: Optional[str] = Field("General Ayurvedic Consultation", description="Requested Ayurvedic treatment")
    notes: Optional[str] = Field(None, description="Any health complaints or notes extracted from the call")


class BookAppointmentResponse(BaseModel):
    status: str = Field(..., example="success")
    confirmation_id: str = Field(..., example="AYUR-7892")
    appointment_id: uuid.UUID
    doctor_name: str
    appointment_time: str
    message: str = Field(..., description="Speech-ready confirmation message for the voice caller")

