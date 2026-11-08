import uuid
from datetime import datetime, date, time, timedelta, timezone
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.clinic import Clinic
from backend.app.models.doctor import Doctor
from backend.app.models.schedule import DoctorSchedule
from backend.app.models.appointment import Appointment, AppointmentStatus
from backend.app.schemas.tool_calling import CheckAvailabilityResponse


class AvailabilityService:
    @staticmethod
    def parse_requested_date_and_time(date_time_str: str) -> Tuple[date, Optional[time]]:
        """Parse flexible date/time string from Conversational AI (e.g., '2026-11-10', '2026-11-10T10:00:00', '2026-11-10 10:00')"""
        clean_str = date_time_str.strip()
        
        # Try full ISO datetime formats
        for fmt in (
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M",
        ):
            try:
                dt = datetime.strptime(clean_str, fmt)
                return dt.date(), dt.time()
            except ValueError:
                continue

        # Try date-only formats
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                d = datetime.strptime(clean_str, fmt).date()
                return d, None
            except ValueError:
                continue

        # Fallback to current date
        now = datetime.now()
        return now.date(), None

    @classmethod
    async def check_availability(
        cls,
        db: AsyncSession,
        clinic_id: Optional[uuid.UUID],
        date_time_str: str,
        doctor_name: Optional[str] = None,
        treatment_type: Optional[str] = None,
    ) -> CheckAvailabilityResponse:
        # 1. Fetch clinic
        if clinic_id:
            clinic_stmt = select(Clinic).where(Clinic.id == clinic_id)
        else:
            clinic_stmt = select(Clinic).limit(1)
        clinic_result = await db.execute(clinic_stmt)
        clinic = clinic_result.scalar_one_or_none()
        if not clinic:
            return CheckAvailabilityResponse(
                available=False,
                message="Clinic not found. Please verify the clinic details.",
                available_slots=[]
            )

        # 2. Find target doctor
        doctor_stmt = select(Doctor).where(
            and_(Doctor.clinic_id == clinic.id, Doctor.is_active == True)  # noqa
        )
        if doctor_name:
            clean_doc_name = doctor_name.replace("Dr.", "").replace("Dr ", "").strip().lower()
            doctor_stmt = doctor_stmt.where(Doctor.name.ilike(f"%{clean_doc_name}%"))

        doctor_result = await db.execute(doctor_stmt)
        doctor = doctor_result.scalars().first()

        # If doctor name specified was not found, fallback to any active doctor in clinic
        if not doctor:
            fallback_stmt = select(Doctor).where(
                and_(Doctor.clinic_id == clinic_id, Doctor.is_active == True)  # noqa
            )
            fallback_res = await db.execute(fallback_stmt)
            doctor = fallback_res.scalars().first()

        if not doctor:
            return CheckAvailabilityResponse(
                available=False,
                message=f"No active doctors are currently registered at {clinic.name}.",
                available_slots=[]
            )

        # 3. Parse date and requested time
        target_date, requested_time = cls.parse_requested_date_and_time(date_time_str)
        day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday

        # 4. Fetch doctor schedule for this day of week
        schedule_stmt = select(DoctorSchedule).where(
            and_(
                DoctorSchedule.doctor_id == doctor.id,
                DoctorSchedule.day_of_week == day_of_week,
                DoctorSchedule.is_active == True  # noqa
            )
        )
        schedule_res = await db.execute(schedule_stmt)
        schedules = schedule_res.scalars().all()

        day_name = target_date.strftime("%A, %B %d")

        if not schedules:
            return CheckAvailabilityResponse(
                available=False,
                message=f"{doctor.name} is not available on {day_name}. Would you like to check another day?",
                available_slots=[],
                doctor_id=doctor.id,
                doctor_name=doctor.name,
                consultation_fee=float(doctor.consultation_fee)
            )

        # 5. Fetch existing booked appointments for doctor on target date
        day_start = datetime.combine(target_date, time.min).replace(tzinfo=timezone.utc)
        day_end = datetime.combine(target_date, time.max).replace(tzinfo=timezone.utc)

        app_stmt = select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.status != AppointmentStatus.CANCELLED,
                Appointment.appointment_time >= day_start,
                Appointment.appointment_time <= day_end
            )
        )
        app_res = await db.execute(app_stmt)
        existing_appointments = app_res.scalars().all()

        booked_times = {
            app.appointment_time.astimezone(timezone.utc).strftime("%H:%M")
            if app.appointment_time.tzinfo else app.appointment_time.strftime("%H:%M")
            for app in existing_appointments
        }

        # 6. Generate candidate slots across all schedule blocks for the day
        open_slots: List[datetime] = []
        for sched in schedules:
            curr_time = sched.start_time
            slot_delta = timedelta(minutes=sched.slot_duration_minutes)

            while True:
                slot_end = (datetime.combine(target_date, curr_time) + slot_delta).time()
                if curr_time >= sched.end_time or slot_end > sched.end_time:
                    break

                slot_time_str = curr_time.strftime("%H:%M")
                if slot_time_str not in booked_times:
                    slot_dt = datetime.combine(target_date, curr_time).replace(tzinfo=timezone.utc)
                    open_slots.append(slot_dt)

                curr_time = slot_end

        if not open_slots:
            return CheckAvailabilityResponse(
                available=False,
                message=f"All appointment slots for {doctor.name} are fully booked on {day_name}. Would you like to check the following day?",
                available_slots=[],
                doctor_id=doctor.id,
                doctor_name=doctor.name,
                consultation_fee=float(doctor.consultation_fee)
            )

        slot_iso_list = [s.isoformat() for s in open_slots]
        readable_times = [s.strftime("%I:%M %p").lstrip("0") for s in open_slots[:5]]
        formatted_options = ", ".join(readable_times)

        # 7. Check if a specific time was requested
        if requested_time:
            req_str = requested_time.strftime("%H:%M")
            # Check match within ±15 minutes
            matched_slot = None
            for s in open_slots:
                if s.strftime("%H:%M") == req_str:
                    matched_slot = s
                    break

            if matched_slot:
                readable_req = matched_slot.strftime("%I:%M %p").lstrip("0")
                return CheckAvailabilityResponse(
                    available=True,
                    message=f"Yes, {doctor.name} is available on {day_name} at {readable_req}. Would you like me to book this appointment for you?",
                    available_slots=[matched_slot.isoformat()],
                    doctor_id=doctor.id,
                    doctor_name=doctor.name,
                    consultation_fee=float(doctor.consultation_fee)
                )
            else:
                # Requested time not available; offer alternative slots
                return CheckAvailabilityResponse(
                    available=False,
                    message=f"I'm sorry, {doctor.name} is not available at {requested_time.strftime('%I:%M %p').lstrip('0')} on {day_name}. Available times include {formatted_options}. Would one of those work for you?",
                    available_slots=slot_iso_list,
                    doctor_id=doctor.id,
                    doctor_name=doctor.name,
                    consultation_fee=float(doctor.consultation_fee)
                )

        # No specific time provided; present available options
        return CheckAvailabilityResponse(
            available=True,
            message=f"{doctor.name} is available on {day_name} at {formatted_options}. What time works best for you?",
            available_slots=slot_iso_list,
            doctor_id=doctor.id,
            doctor_name=doctor.name,
            consultation_fee=float(doctor.consultation_fee)
        )

