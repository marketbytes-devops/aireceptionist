import logging
from typing import Optional
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def send_appointment_sms(
        patient_phone: str,
        patient_name: str,
        doctor_name: str,
        clinic_name: str,
        appointment_time_str: str,
        confirmation_code: str
    ) -> bool:
        message_body = (
            f"Namaste {patient_name}, your Ayurvedic appointment at {clinic_name} with {doctor_name} "
            f"is confirmed for {appointment_time_str}. Booking ID: {confirmation_code}. "
            f"Please arrive 10 mins early."
        )

        # Check if Twilio is configured
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
            try:
                from twilio.rest import Client
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                message = client.messages.create(
                    body=message_body,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=patient_phone
                )
                logger.info(f"SMS sent successfully via Twilio SID {message.sid} to {patient_phone}")
                return True
            except Exception as e:
                logger.error(f"Failed to send SMS via Twilio: {str(e)}")
                # Fallback to local log
        
        # Safe simulated log for testing & local development
        logger.info(f"[SIMULATED NOTIFICATION] To: {patient_phone} | Body: {message_body}")
        print(f"\n[NOTIF-DISPATCH] ===> SMS to {patient_phone}:\n{message_body}\n")
        return True

    @staticmethod
    def send_appointment_whatsapp(
        patient_phone: str,
        patient_name: str,
        doctor_name: str,
        clinic_name: str,
        appointment_time_str: str,
        confirmation_code: str
    ) -> bool:
        # Standard WhatsApp format via Twilio WhatsApp Sandbox / API
        formatted_to = f"whatsapp:{patient_phone}" if not patient_phone.startswith("whatsapp:") else patient_phone
        from_number = f"whatsapp:{settings.TWILIO_PHONE_NUMBER}"

        message_body = (
            f"🌿 *{clinic_name} Confirmation*\n\n"
            f"Namaste *{patient_name}*,\n"
            f"Your consultation with *{doctor_name}* has been confirmed.\n"
            f"📅 Time: {appointment_time_str}\n"
            f"🔖 Booking Reference: *{confirmation_code}*\n\n"
            f"To reschedule or cancel, reply to this message or call our receptionist."
        )

        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
            try:
                from twilio.rest import Client
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                msg = client.messages.create(
                    body=message_body,
                    from_=from_number,
                    to=formatted_to
                )
                logger.info(f"WhatsApp sent via Twilio SID {msg.sid} to {formatted_to}")
                return True
            except Exception as e:
                logger.error(f"Failed to send WhatsApp via Twilio: {str(e)}")

        print(f"\n[WHATSAPP-DISPATCH] ===> WhatsApp to {formatted_to}:\n{message_body}\n")
        return True

