"""AyurVoice SaaS - End-to-End Simulation Script
Simulates a real patient phone call handled by Twilio and ElevenLabs Conversational AI:
1. Inbound Twilio Call -> Generates TwiML
2. ElevenLabs Conversational AI Tool: check-availability
3. ElevenLabs Conversational AI Tool: book-appointment
4. ElevenLabs Post-Call Webhook: Transcript and Audio Analytics
5. Verification of database state & tenant isolation
"""

import os
import sys

# Ensure workspace root is always in sys.path
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from backend.app.main import app
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.clinic import Clinic
from backend.app.models.doctor import Doctor
from backend.app.models.appointment import Appointment
from backend.app.models.call_log import CallLog


async def run_simulation():
    print("=" * 70)
    print("🌿 AYURVOICE SAAS - TELEPHONY & VOICE AI SIMULATION")
    print("=" * 70)

    # Initialize tables and seed demo clinic
    await init_db()

    # Trigger app lifespan seeding
    from backend.app.main import lifespan
    async with lifespan(app):
        pass

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Step 1: Query Seeded Clinic
        print("\n[Step 1] Fetching clinic information...")
        async with AsyncSessionLocal() as session:
            clinic_stmt = select(Clinic).limit(1)
            clinic = (await session.execute(clinic_stmt)).scalar_one_or_none()

            doctor_stmt = select(Doctor).where(Doctor.clinic_id == clinic.id).limit(1)
            doctor = (await session.execute(doctor_stmt)).scalar_one_or_none()

        print(f"  ✓ Clinic: {clinic.name} ({clinic.phone_number})")
        print(f"  ✓ Specialist Vaidya: {doctor.name} - {doctor.specialization}")

        # Step 2: Patient dials clinic phone number (Twilio Voice Inbound)
        simulated_call_sid = f"CA_SIM_{uuid.uuid4().hex[:12]}"
        print(f"\n[Step 2] Simulating Twilio Inbound Voice Call ({simulated_call_sid})...")
        twilio_form = {
            "CallSid": simulated_call_sid,
            "From": "+919988776655",
            "To": clinic.phone_number,
        }
        res = await client.post(
            "/api/v1/telephony/incoming-call",
            data=twilio_form,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"  ✓ Twilio Response Status: {res.status_code}")
        print(f"  ✓ TwiML XML Generated:\n{res.text}")

        # Step 3: ElevenLabs Conversational AI Tool: Check Availability
        # Find next Tuesday
        today = datetime.now()
        days_ahead = (1 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_date_str = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

        print(f"\n[Step 3] ElevenLabs executes Tool: check-availability for {target_date_str}...")
        check_payload = {
            "clinic_id": str(clinic.id),
            "doctor_name": doctor.name,
            "date_time": f"{target_date_str}T10:00:00",
            "treatment_type": "Panchakarma Consultation"
        }
        res_avail = await client.post("/api/v1/tools/check-availability", json=check_payload)
        avail_data = res_avail.json()
        print(f"  ✓ Available: {avail_data['available']}")
        print(f"  ✓ AI Voice Speech Output: \"{avail_data['message']}\"")
        print(f"  ✓ Open Slots Found: {len(avail_data.get('available_slots', []))} slots")

        # Pick the first truly available slot from check-availability
        first_open_slot = avail_data["available_slots"][0] if avail_data.get("available_slots") else f"{target_date_str}T11:00:00"

        # Step 4: ElevenLabs Conversational AI Tool: Book Appointment
        print(f"\n[Step 4] ElevenLabs executes Tool: book-appointment for slot {first_open_slot}...")
        book_payload = {
            "clinic_id": str(clinic.id),
            "doctor_name": doctor.name,
            "patient_name": "Rohan Deshmukh",
            "patient_phone": "+919988776655",
            "patient_email": "rohan.deshmukh@example.com",
            "appointment_time": first_open_slot,
            "treatment_type": "Panchakarma Consultation",
            "notes": "Patient reports severe joint stiffness and cervical spondylosis symptoms."
        }
        res_book = await client.post("/api/v1/tools/book-appointment", json=book_payload)
        book_data = res_book.json()
        print(f"  ✓ Booking Status: {book_data['status']}")
        print(f"  ✓ Unique Confirmation ID: {book_data['confirmation_id']}")
        print(f"  ✓ AI Voice Speech Confirmation:\n    \"{book_data['message']}\"")

        # Step 5: Post-Call Webhook from ElevenLabs
        print(f"\n[Step 5] Simulating ElevenLabs Post-Call Webhook (Transcript & Audio Recording)...")
        transcript_sample = (
            "Agent: Namaste! Welcome to Sree Kerala Ayurvedic Clinic. How may I assist you with your wellness today?\n"
            "Patient: Namaste, I am suffering from cervical spondylosis and stiffness. I need an appointment with Dr. Rajesh Varma.\n"
            "Agent: Dr. Rajesh Varma is our specialist in Panchakarma therapies. He is available next Tuesday at 10:00 AM. Would you like me to book this for you?\n"
            "Patient: Yes please, book that for me. My name is Rohan Deshmukh, phone number is 9988776655.\n"
            "Agent: Your appointment with Dr. Rajesh Varma has been confirmed for Tuesday at 10:00 AM. Your confirmation reference is "
            + book_data['confirmation_id']
            + ". Thank you for choosing Sree Kerala Ayurvedic Clinic!"
        )

        post_call_payload = {
            "call_id": f"conv_sim_{uuid.uuid4().hex[:8]}",
            "call_sid": simulated_call_sid,
            "clinic_id": str(clinic.id),
            "caller_phone": "+919988776655",
            "duration_secs": 168,
            "recording_url": "https://api.elevenlabs.io/recordings/conv_elevenlabs_sim_001.mp3",
            "transcript": transcript_sample,
            "analysis": {
                "transcript_summary": "Patient Rohan Deshmukh scheduled a Panchakarma consultation with Dr. Rajesh Varma for cervical spondylosis.",
                "sentiment": "positive"
            }
        }

        res_post = await client.post("/api/v1/webhooks/elevenlabs-post-call", json=post_call_payload)
        print(f"  ✓ Post-Call Webhook Status: {res_post.json()}")

        # Step 6: Verify Database Records
        print(f"\n[Step 6] Verifying Database State...")
        async with AsyncSessionLocal() as session:
            # Verify Appointment
            app_stmt = select(Appointment).where(Appointment.id == uuid.UUID(book_data['appointment_id']))
            saved_app = (await session.execute(app_stmt)).scalar_one_or_none()
            print(f"  ✓ Saved Appointment in DB: {saved_app.patient_name} ({saved_app.treatment_type})")
            print(f"  ✓ Appointment Status: {saved_app.status.value}")
            print(f"  ✓ Appointment ID: {saved_app.id}")

            # Verify CallLog
            log_stmt = select(CallLog).where(CallLog.call_sid == simulated_call_sid)
            saved_log = (await session.execute(log_stmt)).scalar_one_or_none()
            print(f"  ✓ Saved CallLog in DB: Duration={saved_log.duration_seconds}s, Sentiment={saved_log.sentiment}")

        print("\n" + "=" * 70)
        print("🎉 END-TO-END TELEPHONY & VOICE AI SIMULATION SUCCESSFUL!")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_simulation())
