from typing import List, Optional
from pydantic import BaseModel
from backend.app.schemas.appointment import AppointmentResponse
from backend.app.schemas.call_log import CallLogResponse


class DashboardStats(BaseModel):
    total_calls_today: int
    appointments_booked_today: int
    active_doctors: int
    total_patients: int
    recent_appointments: List[AppointmentResponse]
    recent_call_logs: List[CallLogResponse]

