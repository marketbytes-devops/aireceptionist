import uuid
from datetime import datetime, time, timezone
from typing import Any, Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.appointment import Appointment, AppointmentStatus
from backend.app.models.doctor import Doctor
from backend.app.models.call_log import CallLog
from backend.app.schemas.analytics import DashboardStats
from backend.app.schemas.appointment import AppointmentResponse
from backend.app.schemas.call_log import CallLogResponse
from backend.app.api.deps import get_current_clinic_admin, User

router = APIRouter(prefix="/analytics", tags=["Analytics & Dashboard"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_statistics(
    clinic_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_clinic_admin)
) -> Any:
    """Fetch aggregated overview statistics and recent activities for clinic dashboard."""
    effective_clinic_id = current_user.clinic_id or clinic_id

    today_start = datetime.combine(datetime.now(timezone.utc).date(), time.min).replace(tzinfo=timezone.utc)
    today_end = datetime.combine(datetime.now(timezone.utc).date(), time.max).replace(tzinfo=timezone.utc)

    # 1. Total calls today
    call_stmt = select(func.count(CallLog.id)).where(CallLog.created_at >= today_start)
    if effective_clinic_id:
        call_stmt = call_stmt.where(CallLog.clinic_id == effective_clinic_id)
    total_calls_today = (await db.execute(call_stmt)).scalar() or 0

    # 2. Appointments booked today
    app_today_stmt = select(func.count(Appointment.id)).where(
        and_(
            Appointment.created_at >= today_start,
            Appointment.status != AppointmentStatus.CANCELLED
        )
    )
    if effective_clinic_id:
        app_today_stmt = app_today_stmt.where(Appointment.clinic_id == effective_clinic_id)
    appointments_booked_today = (await db.execute(app_today_stmt)).scalar() or 0

    # 3. Active doctors
    doc_stmt = select(func.count(Doctor.id)).where(Doctor.is_active == True)  # noqa
    if effective_clinic_id:
        doc_stmt = doc_stmt.where(Doctor.clinic_id == effective_clinic_id)
    active_doctors = (await db.execute(doc_stmt)).scalar() or 0

    # 4. Total unique patients
    patients_stmt = select(func.count(func.distinct(Appointment.patient_phone)))
    if effective_clinic_id:
        patients_stmt = patients_stmt.where(Appointment.clinic_id == effective_clinic_id)
    total_patients = (await db.execute(patients_stmt)).scalar() or 0

    # 5. Recent 5 appointments
    recent_app_stmt = (
        select(Appointment)
        .options(selectinload(Appointment.doctor), selectinload(Appointment.clinic))
        .order_by(Appointment.appointment_time.desc())
        .limit(5)
    )
    if effective_clinic_id:
        recent_app_stmt = recent_app_stmt.where(Appointment.clinic_id == effective_clinic_id)
    recent_apps = (await db.execute(recent_app_stmt)).scalars().all()

    formatted_apps = [
        AppointmentResponse(
            id=a.id,
            clinic_id=a.clinic_id,
            doctor_id=a.doctor_id,
            patient_name=a.patient_name,
            patient_phone=a.patient_phone,
            patient_email=a.patient_email,
            appointment_time=a.appointment_time,
            status=a.status,
            treatment_type=a.treatment_type,
            notes=a.notes,
            call_transcript=a.call_transcript,
            doctor_name=a.doctor.name if a.doctor else None,
            clinic_name=a.clinic.name if a.clinic else None,
            created_at=a.created_at,
            updated_at=a.updated_at
        )
        for a in recent_apps
    ]

    # 6. Recent 5 call logs
    recent_calls_stmt = select(CallLog).order_by(CallLog.created_at.desc()).limit(5)
    if effective_clinic_id:
        recent_calls_stmt = recent_calls_stmt.where(CallLog.clinic_id == effective_clinic_id)
    recent_calls = (await db.execute(recent_calls_stmt)).scalars().all()

    formatted_calls = [
        CallLogResponse(
            id=c.id,
            clinic_id=c.clinic_id,
            call_sid=c.call_sid,
            caller_phone=c.caller_phone,
            duration_seconds=c.duration_seconds,
            recording_url=c.recording_url,
            transcript=c.transcript,
            summary=c.summary,
            sentiment=c.sentiment,
            outcome=c.outcome,
            appointment_id=c.appointment_id,
            created_at=c.created_at,
            updated_at=c.updated_at
        )
        for c in recent_calls
    ]

    return DashboardStats(
        total_calls_today=total_calls_today,
        appointments_booked_today=appointments_booked_today,
        active_doctors=active_doctors,
        total_patients=total_patients,
        recent_appointments=formatted_apps,
        recent_call_logs=formatted_calls
    )


@router.get("/call-logs", response_model=List[CallLogResponse])
async def list_call_logs(
    clinic_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_clinic_admin)
) -> Any:
    """List call logs with full transcript and recording details."""
    effective_clinic_id = current_user.clinic_id or clinic_id
    stmt = select(CallLog).order_by(CallLog.created_at.desc())
    if effective_clinic_id:
        stmt = stmt.where(CallLog.clinic_id == effective_clinic_id)
    stmt = stmt.offset(skip).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()

