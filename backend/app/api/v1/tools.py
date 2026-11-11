from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.schemas.tool_calling import (
    CheckAvailabilityRequest,
    CheckAvailabilityResponse,
    BookAppointmentRequest,
    BookAppointmentResponse,
    FindAppointmentRequest,
    FindAppointmentResponse,
    RescheduleAppointmentRequest,
    RescheduleAppointmentResponse,
    CancelAppointmentRequest,
    CancelAppointmentResponse,
    EscalateStaffRequest,
    EscalateStaffResponse,
)
from backend.app.services.availability_service import AvailabilityService
from backend.app.services.booking_service import BookingService
from backend.app.services.notification_service import NotificationService

router = APIRouter(prefix="/tools", tags=["ElevenLabs Conversational AI Tools"])


@router.post("/check-availability", response_model=CheckAvailabilityResponse)
async def check_doctor_availability_tool(
    payload: CheckAvailabilityRequest,
    db: AsyncSession = Depends(get_db)
) -> CheckAvailabilityResponse:
    """Check doctor availability for Sreerudra Ayurveda."""
    return await AvailabilityService.check_availability(
        db=db,
        clinic_id=payload.clinic_id,
        date_time_str=payload.date_time,
        doctor_name=payload.doctor_name,
        treatment_type=payload.treatment_type,
    )


@router.post("/book-appointment", response_model=BookAppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment_tool(
    payload: BookAppointmentRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> BookAppointmentResponse:
    """Book an appointment (with patient name, age, phone, doctor/specialty)."""
    booking = await BookingService.book_appointment(
        db=db,
        clinic_id=payload.clinic_id,
        patient_name=payload.patient_name,
        patient_age=payload.patient_age,
        patient_phone=payload.patient_phone,
        appointment_time_str=payload.appointment_time,
        doctor_name=payload.doctor_name,
        patient_email=payload.patient_email,
        treatment_type=payload.treatment_type,
        notes=payload.notes,
    )

    if getattr(settings, "ENABLE_CELERY", False):
        try:
            from backend.app.tasks.notification_tasks import send_booking_notification_task
            send_booking_notification_task.delay(
                patient_phone=payload.patient_phone,
                patient_name=payload.patient_name,
                doctor_name=booking.doctor_name,
                clinic_name="Sreerudra Ayurveda",
                appointment_time_str=booking.appointment_time,
                confirmation_code=booking.confirmation_id,
                send_whatsapp=True
            )
        except Exception:
            background_tasks.add_task(
                NotificationService.send_appointment_sms,
                patient_phone=payload.patient_phone,
                patient_name=payload.patient_name,
                doctor_name=booking.doctor_name,
                clinic_name="Sreerudra Ayurveda",
                appointment_time_str=booking.appointment_time,
                confirmation_code=booking.confirmation_id
            )
    else:
        background_tasks.add_task(
            NotificationService.send_appointment_sms,
            patient_phone=payload.patient_phone,
            patient_name=payload.patient_name,
            doctor_name=booking.doctor_name,
            clinic_name="Sreerudra Ayurveda",
            appointment_time_str=booking.appointment_time,
            confirmation_code=booking.confirmation_id
        )

    return booking


@router.post("/find-appointment", response_model=FindAppointmentResponse)
async def find_appointment_tool(
    payload: FindAppointmentRequest,
    db: AsyncSession = Depends(get_db)
) -> FindAppointmentResponse:
    """Look up an existing booked appointment by phone number, patient name, or confirmation code."""
    return await BookingService.find_appointments(
        db=db,
        clinic_id=payload.clinic_id,
        patient_phone=payload.patient_phone,
        patient_name=payload.patient_name,
        confirmation_code=payload.confirmation_code,
    )


@router.post("/reschedule-appointment", response_model=RescheduleAppointmentResponse)
async def reschedule_appointment_tool(
    payload: RescheduleAppointmentRequest,
    db: AsyncSession = Depends(get_db)
) -> RescheduleAppointmentResponse:
    """Reschedule an existing appointment to a confirmed new date and time."""
    return await BookingService.reschedule_appointment(
        db=db,
        clinic_id=payload.clinic_id,
        appointment_id=payload.appointment_id,
        patient_phone=payload.patient_phone,
        patient_name=payload.patient_name,
        new_appointment_time_str=payload.new_appointment_time,
        doctor_name=payload.doctor_name,
    )


@router.post("/cancel-appointment", response_model=CancelAppointmentResponse)
async def cancel_appointment_tool(
    payload: CancelAppointmentRequest,
    db: AsyncSession = Depends(get_db)
) -> CancelAppointmentResponse:
    """Cancel an existing appointment after explicit confirmation from the caller."""
    return await BookingService.cancel_appointment(
        db=db,
        clinic_id=payload.clinic_id,
        appointment_id=payload.appointment_id,
        patient_phone=payload.patient_phone,
        patient_name=payload.patient_name,
        reason=payload.reason,
    )


@router.post("/escalate-to-staff", response_model=EscalateStaffResponse)
async def escalate_to_staff_tool(
    payload: EscalateStaffRequest,
    db: AsyncSession = Depends(get_db)
) -> EscalateStaffResponse:
    """Log an urgent staff transfer or special inquiry alert for human reception staff."""
    return await BookingService.escalate_to_staff(
        db=db,
        clinic_id=payload.clinic_id,
        patient_name=payload.patient_name or "Caller",
        patient_phone=payload.patient_phone or "Unknown",
        reason=payload.reason,
        urgency=payload.urgency or "normal",
        branch=payload.branch or "Central Desk",
    )
