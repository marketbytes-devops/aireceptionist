import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.doctor import Doctor
from backend.app.models.schedule import DoctorSchedule
from backend.app.models.clinic import Clinic
from backend.app.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorResponse
from backend.app.schemas.schedule import DoctorScheduleCreate, DoctorScheduleUpdate, DoctorScheduleResponse
from backend.app.api.deps import get_current_clinic_admin, User

router = APIRouter(prefix="/doctors", tags=["Doctors & Schedules"])


@router.post("", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    doctor_in: DoctorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_clinic_admin)
) -> Any:
    """Create a new doctor at a clinic."""
    clinic_id = doctor_in.clinic_id or current_user.clinic_id
    if not clinic_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clinic ID must be provided."
        )

    # Multi-tenant security check
    if current_user.clinic_id and current_user.clinic_id != clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create doctor for another clinic."
        )

    doctor = Doctor(
        clinic_id=clinic_id,
        name=doctor_in.name,
        specialization=doctor_in.specialization,
        consultation_fee=doctor_in.consultation_fee,
        bio=doctor_in.bio,
        is_active=doctor_in.is_active
    )
    db.add(doctor)
    await db.flush()

    # If initial schedules were provided, create them
    if doctor_in.initial_schedules:
        for sched in doctor_in.initial_schedules:
            db_sched = DoctorSchedule(
                doctor_id=doctor.id,
                day_of_week=sched.day_of_week,
                start_time=sched.start_time,
                end_time=sched.end_time,
                slot_duration_minutes=sched.slot_duration_minutes,
                is_active=sched.is_active
            )
            db.add(db_sched)

    await db.commit()

    # Re-fetch with loaded schedules
    stmt = select(Doctor).where(Doctor.id == doctor.id).options(selectinload(Doctor.schedules))
    res = await db.execute(stmt)
    return res.scalar_one()


@router.get("", response_model=List[DoctorResponse])
async def list_doctors(
    clinic_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List doctors, optionally filtered by clinic."""
    stmt = select(Doctor).options(selectinload(Doctor.schedules))
    if clinic_id:
        stmt = stmt.where(Doctor.clinic_id == clinic_id)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(
    doctor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get single doctor profile and schedules."""
    stmt = select(Doctor).where(Doctor.id == doctor_id).options(selectinload(Doctor.schedules))
    res = await db.execute(stmt)
    doctor = res.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")
    return doctor


@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: uuid.UUID,
    doctor_in: DoctorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_clinic_admin)
) -> Any:
    """Update doctor information."""
    stmt = select(Doctor).where(Doctor.id == doctor_id).options(selectinload(Doctor.schedules))
    res = await db.execute(stmt)
    doctor = res.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")

    if current_user.clinic_id and current_user.clinic_id != doctor.clinic_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    for field, val in doctor_in.model_dump(exclude_unset=True).items():
        setattr(doctor, field, val)

    await db.commit()
    await db.refresh(doctor)
    return doctor


@router.post("/{doctor_id}/schedules", response_model=DoctorScheduleResponse, status_code=status.HTTP_201_CREATED)
async def add_doctor_schedule(
    doctor_id: uuid.UUID,
    schedule_in: DoctorScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_clinic_admin)
) -> Any:
    """Add a weekly schedule slot to a doctor."""
    stmt = select(Doctor).where(Doctor.id == doctor_id)
    res = await db.execute(stmt)
    doctor = res.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")

    if current_user.clinic_id and current_user.clinic_id != doctor.clinic_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    schedule = DoctorSchedule(
        doctor_id=doctor_id,
        day_of_week=schedule_in.day_of_week,
        start_time=schedule_in.start_time,
        end_time=schedule_in.end_time,
        slot_duration_minutes=schedule_in.slot_duration_minutes,
        is_active=schedule_in.is_active
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule


@router.delete("/{doctor_id}/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor_schedule(
    doctor_id: uuid.UUID,
    schedule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_clinic_admin)
) -> None:
    """Remove a doctor schedule."""
    stmt = select(DoctorSchedule).where(
        and_(DoctorSchedule.id == schedule_id, DoctorSchedule.doctor_id == doctor_id)
    )
    res = await db.execute(stmt)
    schedule = res.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found.")

    await db.delete(schedule)
    await db.commit()

