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
    patient_age: Optional[str] = Field(None, description="Patient age in years, e.g. '42'")
    patient_phone: str = Field(..., description="Patient contact phone number with country code")
    patient_email: Optional[str] = Field(None, description="Optional patient email for notifications")
    appointment_time: str = Field(..., description="Confirmed ISO datetime string for the booking")
    treatment_type: Optional[str] = Field("General Ayurvedic Consultation", description="Requested Ayurvedic treatment or specialty")
    notes: Optional[str] = Field(None, description="Any health complaints, branch preference, or notes extracted from the call")


class BookAppointmentResponse(BaseModel):
    status: str = Field(..., example="success")
    confirmation_id: str = Field(..., example="AYUR-7892")
    appointment_id: uuid.UUID
    doctor_name: str
    appointment_time: str
    message: str = Field(..., description="Speech-ready confirmation message for the voice caller")


class FindAppointmentRequest(BaseModel):
    clinic_id: Optional[uuid.UUID] = Field(None, description="Optional clinic ID")
    patient_phone: Optional[str] = Field(None, description="Patient phone number used when booking")
    patient_name: Optional[str] = Field(None, description="Patient name for verification")
    confirmation_code: Optional[str] = Field(None, description="Optional confirmation code like AYUR-1234")


class MatchedAppointmentInfo(BaseModel):
    appointment_id: uuid.UUID
    patient_name: str
    patient_phone: str
    doctor_name: str
    appointment_time: str
    treatment_type: str
    status: str


class FindAppointmentResponse(BaseModel):
    found: bool
    appointments: List[MatchedAppointmentInfo] = Field(default=[])
    message: str = Field(..., description="Speech-ready summary of found appointment(s)")


class RescheduleAppointmentRequest(BaseModel):
    clinic_id: Optional[uuid.UUID] = Field(None, description="Optional clinic ID")
    appointment_id: Optional[uuid.UUID] = Field(None, description="Appointment UUID found via find_appointment")
    patient_phone: Optional[str] = Field(None, description="Patient phone number if appointment_id not known")
    patient_name: Optional[str] = Field(None, description="Patient name for verification")
    new_appointment_time: str = Field(..., description="Confirmed new ISO datetime string for the rescheduled slot")
    doctor_name: Optional[str] = Field(None, description="Optional new doctor name if changing doctors")


class RescheduleAppointmentResponse(BaseModel):
    status: str
    appointment_id: Optional[uuid.UUID] = None
    doctor_name: Optional[str] = None
    new_appointment_time: Optional[str] = None
    message: str


class CancelAppointmentRequest(BaseModel):
    clinic_id: Optional[uuid.UUID] = Field(None, description="Optional clinic ID")
    appointment_id: Optional[uuid.UUID] = Field(None, description="Appointment UUID found via find_appointment")
    patient_phone: Optional[str] = Field(None, description="Patient phone number if appointment_id not known")
    patient_name: Optional[str] = Field(None, description="Patient name for verification")
    reason: Optional[str] = Field(None, description="Reason for cancelling the appointment")


class CancelAppointmentResponse(BaseModel):
    status: str
    appointment_id: Optional[uuid.UUID] = None
    message: str


class EscalateStaffRequest(BaseModel):
    clinic_id: Optional[uuid.UUID] = Field(None, description="Optional clinic ID")
    patient_name: Optional[str] = Field("Caller", description="Name of the caller")
    patient_phone: Optional[str] = Field("Unknown", description="Callback phone number")
    reason: str = Field(..., description="Reason for staff transfer or emergency details")
    urgency: Optional[str] = Field("normal", description="'normal' or 'emergency'")
    branch: Optional[str] = Field("Central Desk", description="Alappuzha, Trivandrum, or Central Desk")


class EscalateStaffResponse(BaseModel):
    status: str
    ticket_id: str
    helpline_number: str
    message: str


