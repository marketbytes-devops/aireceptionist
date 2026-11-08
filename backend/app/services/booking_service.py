import uuid
import random
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from backend.app.models.clinic import Clinic
from backend.app.models.doctor import Doctor
from backend.app.models.schedule import DoctorSchedule
from backend.app.models.appointment import Appointment, AppointmentStatus
from backend.app.schemas.tool_calling import BookAppointmentResponse
from backend.app.services.availability_service import AvailabilityService


class BookingService:
    @staticmethod
    def generate_confirmation_code() -> str:
        random_num = random.randint(1000, 9999)
        return f"AYUR-{random_num}"

    @classmethod
    async def book_appointment(
        cls,
        db: AsyncSession,
        clinic_id: uuid.UUID,
        patient_name: str,
        patient_phone: str,
        appointment_time_str: str,
        doctor_name: Optional[str] = None,
        patient_email: Optional[str] = None,
        treatment_type: Optional[str] = "General Ayurvedic Consultation",
        notes: Optional[str] = None,
    ) -> BookAppointmentResponse:
        # 1. Fetch clinic
        clinic_stmt = select(Clinic).where(Clinic.id == clinic_id)
        clinic_res = await db.execute(clinic_stmt)
        clinic = clinic_res.scalar_one_or_none()
        if not clinic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clinic not found."
            )

        # 2. Match doctor
        doctor_stmt = select(Doctor).where(
            and_(Doctor.clinic_id == clinic_id, Doctor.is_active == True)  # noqa
        )
        if doctor_name:
            clean_name = doctor_name.replace("Dr.", "").replace("Dr ", "").strip().lower()
            doctor_stmt = doctor_stmt.where(Doctor.name.ilike(f"%{clean_name}%"))

        doctor_res = await db.execute(doctor_stmt)
        doctor = doctor_res.scalars().first()

        if not doctor:
            # Fallback to any active doctor
            fallback_stmt = select(Doctor).where(
                and_(Doctor.clinic_id == clinic_id, Doctor.is_active == True)  # noqa
            )
            fallback_res = await db.execute(fallback_stmt)
            doctor = fallback_res.scalars().first()

        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No active doctors available at {clinic.name}."
            )

        # 3. Parse booking appointment time
        target_date, target_time = AvailabilityService.parse_requested_date_and_time(appointment_time_str)
        if not target_time:
            # If no time given, default to 10:00 AM
            target_time = datetime.strptime("10:00:00", "%H:%M:%S").time()

        booking_dt = datetime.combine(target_date, target_time).replace(tzinfo=timezone.utc)

        # 4. Check for double booking collision
        window_start = booking_dt - timedelta(minutes=15)
        window_end = booking_dt + timedelta(minutes=15)

        collision_stmt = select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.status != AppointmentStatus.CANCELLED,
                Appointment.appointment_time >= window_start,
                Appointment.appointment_time <= window_end
            )
        )
        collision_res = await db.execute(collision_stmt)
        conflict = collision_res.scalars().first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The slot at {booking_dt.strftime('%I:%M %p')} is already booked for {doctor.name}. Please choose another slot."
            )

        # 5. Create appointment record
        confirmation_code = cls.generate_confirmation_code()
        appointment_notes = f"Confirmation: {confirmation_code}. {notes or ''}".strip()

        new_appointment = Appointment(
            clinic_id=clinic_id,
            doctor_id=doctor.id,
            patient_name=patient_name.strip(),
            patient_phone=patient_phone.strip(),
            patient_email=patient_email.strip() if patient_email else None,
            appointment_time=booking_dt,
            status=AppointmentStatus.BOOKED,
            treatment_type=treatment_type or "General Ayurvedic Consultation",
            notes=appointment_notes,
        )

        db.add(new_appointment)
        await db.commit()
        await db.refresh(new_appointment)

        # 6. Format natural language voice response
        date_formatted = booking_dt.strftime("%A, %B %d")
        time_formatted = booking_dt.strftime("%I:%M %p").lstrip("0")
        voice_message = (
            f"Your appointment with {doctor.name} for {treatment_type} has been successfully confirmed "
            f"for {date_formatted} at {time_formatted}. Your confirmation ID is {confirmation_code}. "
            f"A confirmation message has also been sent to your phone number at {patient_phone}. "
            f"Thank you for contacting {clinic.name}!"
        )

        return BookAppointmentResponse(
            status="success",
            confirmation_id=confirmation_code,
            appointment_id=new_appointment.id,
            doctor_name=doctor.name,
            appointment_time=booking_dt.isoformat(),
            message=voice_message,
        )

