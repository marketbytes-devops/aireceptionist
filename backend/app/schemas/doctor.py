import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from backend.app.schemas.schedule import DoctorScheduleResponse, DoctorScheduleCreate


class DoctorBase(BaseModel):
    name: str = Field(..., example="Dr. Varma")
    specialization: str = Field(..., example="Panchakarma & Pulse Diagnosis Specialist")
    consultation_fee: Decimal = Field(Decimal("500.00"), example=500.00)
    bio: Optional[str] = Field(None, example="BAMS, MD (Ayurveda) with 15+ years experience.")
    is_active: bool = Field(True, example=True)


class DoctorCreate(DoctorBase):
    clinic_id: Optional[uuid.UUID] = None
    initial_schedules: Optional[List[DoctorScheduleCreate]] = None


class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    specialization: Optional[str] = None
    consultation_fee: Optional[Decimal] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None


class DoctorResponse(DoctorBase):
    id: uuid.UUID
    clinic_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    schedules: Optional[List[DoctorScheduleResponse]] = []

    class Config:
        from_attributes = True

