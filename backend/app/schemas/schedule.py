import uuid
from datetime import time, datetime
from typing import Optional
from pydantic import BaseModel, Field


class DoctorScheduleBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday", example=0)
    start_time: time = Field(..., example="09:00:00")
    end_time: time = Field(..., example="17:00:00")
    slot_duration_minutes: int = Field(30, ge=10, le=120, example=30)
    is_active: bool = Field(True, example=True)


class DoctorScheduleCreate(DoctorScheduleBase):
    doctor_id: Optional[uuid.UUID] = None


class DoctorScheduleUpdate(BaseModel):
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    slot_duration_minutes: Optional[int] = Field(None, ge=10, le=120)
    is_active: Optional[bool] = None


class DoctorScheduleResponse(DoctorScheduleBase):
    id: uuid.UUID
    doctor_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

