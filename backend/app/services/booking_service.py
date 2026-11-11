import uuid
import re
import random
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from backend.app.models.clinic import Clinic
from backend.app.models.doctor import Doctor
from backend.app.models.appointment import Appointment, AppointmentStatus
from backend.app.models.call_log import CallLog
from backend.app.schemas.tool_calling import (
    BookAppointmentResponse,
    FindAppointmentResponse,
    MatchedAppointmentInfo,
    RescheduleAppointmentResponse,
    CancelAppointmentResponse,
    EscalateStaffResponse,
)
from backend.app.services.availability_service import AvailabilityService


class BookingService:
    @staticmethod
    def generate_confirmation_code() -> str:
        random_num = random.randint(1000, 9999)
        return f"AYUR-{random_num}"

    @staticmethod
    def normalize_phone_last10(phone: Optional[str]) -> str:
        if not phone:
            return ""
        digits = re.sub(r"\D", "", phone)
        return digits[-10:] if len(digits) >= 10 else digits

    @staticmethod
    async def _resolve_clinic(db: AsyncSession, clinic_id: Optional[uuid.UUID]) -> Clinic:
        if clinic_id:
            clinic_stmt = select(Clinic).where(Clinic.id == clinic_id)
        else:
            clinic_stmt = select(Clinic).limit(1)
        clinic_res = await db.execute(clinic_stmt)
        clinic = clinic_res.scalar_one_or_none()
        if not clinic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clinic not found."
            )
        return clinic

    @classmethod
    async def _resolve_doctor(cls, db: AsyncSession, clinic_id: uuid.UUID, doctor_name: Optional[str]) -> Doctor:
        doctor_stmt = select(Doctor).where(
            and_(Doctor.clinic_id == clinic_id, Doctor.is_active == True)  # noqa
        )
        if doctor_name:
            clean_name = doctor_name.replace("Dr.", "").replace("Dr ", "").strip().lower()
            doctor_stmt = doctor_stmt.where(Doctor.name.ilike(f"%{clean_name}%"))

        doctor_res = await db.execute(doctor_stmt)
        doctor = doctor_res.scalars().first()

        if not doctor:
            fallback_stmt = select(Doctor).where(
                and_(Doctor.clinic_id == clinic_id, Doctor.is_active == True)  # noqa
            )
            fallback_res = await db.execute(fallback_stmt)
            doctor = fallback_res.scalars().first()

        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active doctors available at this clinic."
            )
        return doctor

    @classmethod
    async def book_appointment(
        cls,
        db: AsyncSession,
        clinic_id: Optional[uuid.UUID],
        patient_name: str,
        patient_phone: str,
        appointment_time_str: str,
        doctor_name: Optional[str] = None,
        patient_age: Optional[str] = None,
        patient_email: Optional[str] = None,
        treatment_type: Optional[str] = "General Ayurvedic Consultation",
        notes: Optional[str] = None,
    ) -> BookAppointmentResponse:
        # 1. Fetch clinic
        clinic = await cls._resolve_clinic(db, clinic_id)

        # 2. Match doctor
        doctor = await cls._resolve_doctor(db, clinic.id, doctor_name)

        # 3. Parse booking appointment time
        target_date, target_time = AvailabilityService.parse_requested_date_and_time(appointment_time_str)
        if not target_time:
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

        # 5. Create appointment record with Age & Confirmation Code
        confirmation_code = cls.generate_confirmation_code()
        age_segment = f"Age: {patient_age.strip()} yrs | " if patient_age else ""
        notes_body = notes.strip() if notes else ""
        appointment_notes = f"Confirmation: {confirmation_code} | {age_segment}{notes_body}".strip(" |")

        new_appointment = Appointment(
            clinic_id=clinic.id,
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
            f"Thank you for choosing {clinic.name}!"
        )

        return BookAppointmentResponse(
            status="success",
            confirmation_id=confirmation_code,
            appointment_id=new_appointment.id,
            doctor_name=doctor.name,
            appointment_time=booking_dt.isoformat(),
            message=voice_message,
        )

    @classmethod
    async def find_appointments(
        cls,
        db: AsyncSession,
        clinic_id: Optional[uuid.UUID] = None,
        patient_phone: Optional[str] = None,
        patient_name: Optional[str] = None,
        confirmation_code: Optional[str] = None,
    ) -> FindAppointmentResponse:
        clinic = await cls._resolve_clinic(db, clinic_id)

        stmt = (
            select(Appointment)
            .where(
                and_(
                    Appointment.clinic_id == clinic.id,
                    Appointment.status == AppointmentStatus.BOOKED,
                )
            )
            .options(selectinload(Appointment.doctor))
            .order_by(Appointment.appointment_time.desc())
        )

        res = await db.execute(stmt)
        all_booked = res.scalars().all()

        phone_tail = cls.normalize_phone_last10(patient_phone)
        matches: List[Appointment] = []

        for app in all_booked:
            if confirmation_code and app.notes and confirmation_code.upper() in app.notes.upper():
                matches.append(app)
                continue
            if phone_tail and cls.normalize_phone_last10(app.patient_phone) == phone_tail:
                matches.append(app)
                continue
            if not phone_tail and patient_name and patient_name.strip().lower() in app.patient_name.lower():
                matches.append(app)

        if not matches:
            return FindAppointmentResponse(
                found=False,
                appointments=[],
                message=(
                    "I could not find an active booked appointment matching those details. "
                    "Could you verify the phone number or confirmation code used during booking?"
                ),
            )

        matched_dtos = [
            MatchedAppointmentInfo(
                appointment_id=m.id,
                patient_name=m.patient_name,
                patient_phone=m.patient_phone,
                doctor_name=m.doctor.name if m.doctor else "Specialist Doctor",
                appointment_time=m.appointment_time.isoformat(),
                treatment_type=m.treatment_type or "Ayurvedic Consultation",
                status=m.status.value if hasattr(m.status, "value") else str(m.status),
            )
            for m in matches[:3]
        ]

        first = matched_dtos[0]
        dt_obj = matches[0].appointment_time
        dt_friendly = dt_obj.strftime("%A, %B %d at %I:%M %p").lstrip("0")

        return FindAppointmentResponse(
            found=True,
            appointments=matched_dtos,
            message=(
                f"I found an active appointment for {first.patient_name} with {first.doctor_name} "
                f"for {first.treatment_type} scheduled on {dt_friendly}."
            ),
        )

    @classmethod
    async def _locate_single_appointment(
        cls,
        db: AsyncSession,
        clinic_id: uuid.UUID,
        appointment_id: Optional[uuid.UUID],
        patient_phone: Optional[str],
        patient_name: Optional[str],
    ) -> Optional[Appointment]:
        if appointment_id:
            stmt = (
                select(Appointment)
                .where(Appointment.id == appointment_id)
                .options(selectinload(Appointment.doctor))
            )
            res = await db.execute(stmt)
            return res.scalar_one_or_none()

        found_res = await cls.find_appointments(
            db=db,
            clinic_id=clinic_id,
            patient_phone=patient_phone,
            patient_name=patient_name,
        )
        if not found_res.found or not found_res.appointments:
            return None

        target_id = found_res.appointments[0].appointment_id
        stmt = (
            select(Appointment)
            .where(Appointment.id == target_id)
            .options(selectinload(Appointment.doctor))
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @classmethod
    async def reschedule_appointment(
        cls,
        db: AsyncSession,
        clinic_id: Optional[uuid.UUID],
        new_appointment_time_str: str,
        appointment_id: Optional[uuid.UUID] = None,
        patient_phone: Optional[str] = None,
        patient_name: Optional[str] = None,
        doctor_name: Optional[str] = None,
    ) -> RescheduleAppointmentResponse:
        clinic = await cls._resolve_clinic(db, clinic_id)
        app = await cls._locate_single_appointment(
            db, clinic.id, appointment_id, patient_phone, patient_name
        )

        if not app:
            return RescheduleAppointmentResponse(
                status="not_found",
                message="Could not locate an active appointment to reschedule. Please verify patient phone number or name."
            )

        target_doctor = app.doctor
        if doctor_name:
            target_doctor = await cls._resolve_doctor(db, clinic.id, doctor_name)
            app.doctor_id = target_doctor.id

        target_date, target_time = AvailabilityService.parse_requested_date_and_time(new_appointment_time_str)
        if not target_time:
            target_time = datetime.strptime("10:00:00", "%H:%M:%S").time()

        new_dt = datetime.combine(target_date, target_time).replace(tzinfo=timezone.utc)

        # Check double-booking excluding current appointment
        window_start = new_dt - timedelta(minutes=15)
        window_end = new_dt + timedelta(minutes=15)
        collision_stmt = select(Appointment).where(
            and_(
                Appointment.id != app.id,
                Appointment.doctor_id == app.doctor_id,
                Appointment.status != AppointmentStatus.CANCELLED,
                Appointment.appointment_time >= window_start,
                Appointment.appointment_time <= window_end
            )
        )
        conflict = (await db.execute(collision_stmt)).scalars().first()
        if conflict:
            return RescheduleAppointmentResponse(
                status="conflict",
                appointment_id=app.id,
                message=f"The requested slot at {new_dt.strftime('%I:%M %p')} is already occupied. Please select another time."
            )

        old_dt_str = app.appointment_time.strftime("%b %d %I:%M %p")
        app.appointment_time = new_dt
        app.notes = f"{app.notes or ''} | Rescheduled from {old_dt_str}".strip(" |")
        await db.commit()
        await db.refresh(app)

        doc_name = target_doctor.name if target_doctor else "Specialist Doctor"
        date_fmt = new_dt.strftime("%A, %B %d at %I:%M %p").lstrip("0")

        return RescheduleAppointmentResponse(
            status="success",
            appointment_id=app.id,
            doctor_name=doc_name,
            new_appointment_time=new_dt.isoformat(),
            message=(
                f"Your appointment for {app.patient_name} with {doc_name} has been successfully "
                f"rescheduled to {date_fmt}."
            ),
        )

    @classmethod
    async def cancel_appointment(
        cls,
        db: AsyncSession,
        clinic_id: Optional[uuid.UUID],
        appointment_id: Optional[uuid.UUID] = None,
        patient_phone: Optional[str] = None,
        patient_name: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> CancelAppointmentResponse:
        clinic = await cls._resolve_clinic(db, clinic_id)
        app = await cls._locate_single_appointment(
            db, clinic.id, appointment_id, patient_phone, patient_name
        )

        if not app:
            return CancelAppointmentResponse(
                status="not_found",
                message="Could not find an active booked appointment to cancel. Please recheck your phone number."
            )

        app.status = AppointmentStatus.CANCELLED
        reason_text = f"Cancelled via AI Receptionist ({reason})" if reason else "Cancelled via AI Receptionist"
        app.notes = f"{app.notes or ''} | {reason_text}".strip(" |")
        await db.commit()

        return CancelAppointmentResponse(
            status="success",
            appointment_id=app.id,
            message=f"The appointment for {app.patient_name} has been cancelled as requested.",
        )

    @classmethod
    async def escalate_to_staff(
        cls,
        db: AsyncSession,
        clinic_id: Optional[uuid.UUID],
        patient_name: str,
        patient_phone: str,
        reason: str,
        urgency: str = "normal",
        branch: str = "Central Desk",
    ) -> EscalateStaffResponse:
        clinic = await cls._resolve_clinic(db, clinic_id)
        ticket_id = f"ESC-{random.randint(1000, 9999)}"

        new_log = CallLog(
            clinic_id=clinic.id,
            call_sid=ticket_id,
            caller_phone=patient_phone or "Web/Caller",
            duration_seconds=0,
            summary=f"[{urgency.upper()} STAFF TRANSFER - {branch}] {patient_name}: {reason}",
            transcript=f"Caller ({patient_name}, {patient_phone}) requested staff transfer / emergency assistance.\nReason: {reason}\nBranch: {branch}",
            sentiment="urgent" if urgency == "emergency" else "neutral",
            outcome="escalated_to_staff",
        )
        db.add(new_log)
        await db.commit()

        helpline = "+91 90379 03333"
        if "alappuzha" in branch.lower():
            helpline = "+91 98479 48218"
        elif "trivandrum" in branch.lower() or "thiruvananthapuram" in branch.lower():
            helpline = "+91 95677 48218"

        return EscalateStaffResponse(
            status="escalated",
            ticket_id=ticket_id,
            helpline_number=helpline,
            message=(
                f"I have flagged your request ({ticket_id}) immediately for our hospital staff desk. "
                f"You can also reach our direct helpline at {helpline} right away."
            ),
        )
