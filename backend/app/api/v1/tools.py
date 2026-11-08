from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.schemas.tool_calling import (
    CheckAvailabilityRequest,
    CheckAvailabilityResponse,
    BookAppointmentRequest,
    BookAppointmentResponse,
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
    """ElevenLabs Conversational AI Custom Tool: Check doctor availability for a clinic.
    
    Called dynamically by ElevenLabs Agent during a voice call when the patient asks
    about booking, doctor schedule, or specific date/time.
    """
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
    """ElevenLabs Conversational AI Custom Tool: Book an appointment.
    
    Called dynamically by ElevenLabs Agent once patient confirms preferred time, name,
    and phone number. Atomically reserves the slot and schedules patient notification.
    """
    booking = await BookingService.book_appointment(
        db=db,
        clinic_id=payload.clinic_id,
        patient_name=payload.patient_name,
        patient_phone=payload.patient_phone,
        appointment_time_str=payload.appointment_time,
        doctor_name=payload.doctor_name,
        patient_email=payload.patient_email,
        treatment_type=payload.treatment_type,
        notes=payload.notes,
    )

    # Dispatch asynchronous notification: Celery if enabled, otherwise FastAPI background_tasks
    if getattr(settings, "ENABLE_CELERY", False):
        try:
            from backend.app.tasks.notification_tasks import send_booking_notification_task
            send_booking_notification_task.delay(
                patient_phone=payload.patient_phone,
                patient_name=payload.patient_name,
                doctor_name=booking.doctor_name,
                clinic_name="Ayurvedic Clinic",
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
                clinic_name="Ayurvedic Clinic",
                appointment_time_str=booking.appointment_time,
                confirmation_code=booking.confirmation_id
            )
    else:
        background_tasks.add_task(
            NotificationService.send_appointment_sms,
            patient_phone=payload.patient_phone,
            patient_name=payload.patient_name,
            doctor_name=booking.doctor_name,
            clinic_name="Ayurvedic Clinic",
            appointment_time_str=booking.appointment_time,
            confirmation_code=booking.confirmation_id
        )

    return booking
