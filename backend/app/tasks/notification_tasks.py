import logging
from backend.app.tasks.celery_app import celery_app
from backend.app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


@celery_app.task(name="send_booking_notification_task")
def send_booking_notification_task(
    patient_phone: str,
    patient_name: str,
    doctor_name: str,
    clinic_name: str,
    appointment_time_str: str,
    confirmation_code: str,
    send_whatsapp: bool = False
):
    logger.info(f"Executing Celery task: send_booking_notification to {patient_phone}")
    
    NotificationService.send_appointment_sms(
        patient_phone=patient_phone,
        patient_name=patient_name,
        doctor_name=doctor_name,
        clinic_name=clinic_name,
        appointment_time_str=appointment_time_str,
        confirmation_code=confirmation_code
    )

    if send_whatsapp:
        NotificationService.send_appointment_whatsapp(
            patient_phone=patient_phone,
            patient_name=patient_name,
            doctor_name=doctor_name,
            clinic_name=clinic_name,
            appointment_time_str=appointment_time_str,
            confirmation_code=confirmation_code
        )

    return {"status": "sent", "phone": patient_phone, "code": confirmation_code}

