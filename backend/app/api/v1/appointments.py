import uuid
from datetime import datetime
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.appointment import Appointment, AppointmentStatus
from backend.app.models.doctor import Doctor
from backend.app.models.clinic import Clinic
from backend.app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from backend.app.api.deps import get_current_clinic_admin, User

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.get("", response_model=List[AppointmentResponse])
async def list_appointments(
    clinic_id: Optional[uuid.UUID] = None,
    doctor_id: Optional[uuid.UUID] = None,
    status_filter: Optional[AppointmentStatus] = Query(None, alias="status"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_clinic_admin)
) -> Any:
    """List appointments with filtering options."""
    effective_clinic_id = current_user.clinic_id or clinic_id
    stmt = (
        select(Appointment)
        .options(selectinload(Appointment.doctor), selectinload(Appointment.clinic))
        .order_by(Appointment.appointment_time.desc())
    )

    conditions = []
    if effective_clinic_id:
        conditions.append(Appointment.clinic_id == effective_clinic_id)
    if doctor_id:
        conditions.append(Appointment.doctor_id == doctor_id)
    if status_filter:
        conditions.append(Appointment.status == status_filter)
    if start_date:
        conditions.append(Appointment.appointment_time >= start_date)
    if end_date:
        conditions.append(Appointment.appointment_time <= end_date)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    stmt = stmt.offset(skip).limit(limit)
    res = await db.execute(stmt)
    appointments = res.scalars().all()

    # Populate doctor_name & clinic_name in response
    results = []
    for app in appointments:
        res_item = AppointmentResponse(
            id=app.id,
            clinic_id=app.clinic_id,
            doctor_id=app.doctor_id,
            patient_name=app.patient_name,
            patient_phone=app.patient_phone,
            patient_email=app.patient_email,
            appointment_time=app.appointment_time,
            status=app.status,
            treatment_type=app.treatment_type,
            notes=app.notes,
            call_transcript=app.call_transcript,
            doctor_name=app.doctor.name if app.doctor else None,
            clinic_name=app.clinic.name if app.clinic else None,
            created_at=app.created_at,
            updated_at=app.updated_at
        )
        results.append(res_item)
    return results


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_clinic_admin)
) -> Any:
    """Get single appointment with doctor and clinic details."""
    stmt = (
        select(Appointment)
        .where(Appointment.id == appointment_id)
        .options(selectinload(Appointment.doctor), selectinload(Appointment.clinic))
    )
    res = await db.execute(stmt)
    app = res.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")

    if current_user.clinic_id and current_user.clinic_id != app.clinic_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    return AppointmentResponse(
        id=app.id,
        clinic_id=app.clinic_id,
        doctor_id=app.doctor_id,
        patient_name=app.patient_name,
        patient_phone=app.patient_phone,
        patient_email=app.patient_email,
        appointment_time=app.appointment_time,
        status=app.status,
        treatment_type=app.treatment_type,
        notes=app.notes,
        call_transcript=app.call_transcript,
        doctor_name=app.doctor.name if app.doctor else None,
        clinic_name=app.clinic.name if app.clinic else None,
        created_at=app.created_at,
        updated_at=app.updated_at
    )


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
async def update_appointment_status(
    appointment_id: uuid.UUID,
    update_in: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_clinic_admin)
) -> Any:
    """Update appointment status (e.g. mark completed or cancelled)."""
    stmt = (
        select(Appointment)
        .where(Appointment.id == appointment_id)
        .options(selectinload(Appointment.doctor), selectinload(Appointment.clinic))
    )
    res = await db.execute(stmt)
    app = res.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")

    if current_user.clinic_id and current_user.clinic_id != app.clinic_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if update_in.status:
        app.status = update_in.status
    if update_in.notes:
        app.notes = update_in.notes
    if update_in.call_transcript:
        app.call_transcript = update_in.call_transcript

    await db.commit()
    await db.refresh(app)

    return AppointmentResponse(
        id=app.id,
        clinic_id=app.clinic_id,
        doctor_id=app.doctor_id,
        patient_name=app.patient_name,
        patient_phone=app.patient_phone,
        patient_email=app.patient_email,
        appointment_time=app.appointment_time,
        status=app.status,
        treatment_type=app.treatment_type,
        notes=app.notes,
        call_transcript=app.call_transcript,
        doctor_name=app.doctor.name if app.doctor else None,
        clinic_name=app.clinic.name if app.clinic else None,
        created_at=app.created_at,
        updated_at=app.updated_at
    )

