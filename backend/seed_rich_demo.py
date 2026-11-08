"""AyurVoice SaaS - Rich Demonstration Data Seeder
Populates the database with realistic Ayurvedic clinical data:
- Sree Kerala Ayurvedic Clinic
- 2 Specialist Vaidyas (Panchakarma and Ayurvedic Dietetics)
- Weekly schedules across all 6 working days
- 6 realistic patient appointments across statuses (booked, completed, cancelled)
- 6 recorded patient phone interactions with speaker-turn transcripts and sentiment scores
"""

import asyncio
import uuid
from decimal import Decimal
from datetime import datetime, date, time, timedelta, timezone
from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.core.security import get_password_hash
from backend.app.models.clinic import Clinic
from backend.app.models.doctor import Doctor
from backend.app.models.schedule import DoctorSchedule
from backend.app.models.appointment import Appointment, AppointmentStatus
from backend.app.models.call_log import CallLog
from backend.app.models.user import User, UserRole


async def seed_rich_data():
    print("🌿 Seeding rich demonstration data for AyurVoice SaaS...")
    await init_db()

    async with AsyncSessionLocal() as session:
        # 1. Fetch or create Clinic
        clinic_stmt = select(Clinic).where(Clinic.slug == "sree-kerala-ayurveda")
        clinic = (await session.execute(clinic_stmt)).scalar_one_or_none()

        if not clinic:
            clinic = Clinic(
                name="Sree Kerala Ayurvedic Clinic",
                slug="sree-kerala-ayurveda",
                phone_number="+18005550199",
                address="108 Dhanwantari Road, Fort Kochi, Kerala, 682001",
                timezone="Asia/Kolkata"
            )
            session.add(clinic)
            await session.flush()

        # 2. Ensure Admin User
        user_stmt = select(User).where(User.email == "admin@ayurvoice.com")
        admin_user = (await session.execute(user_stmt)).scalar_one_or_none()
        if not admin_user:
            admin_user = User(
                email="admin@ayurvoice.com",
                hashed_password=get_password_hash("AyurVoice2026!"),
                full_name="Dr. Rajesh Varma",
                role=UserRole.CLINIC_ADMIN,
                clinic_id=clinic.id,
                is_active=True
            )
            session.add(admin_user)

        # 3. Ensure Doctors
        doc_stmt = select(Doctor).where(Doctor.clinic_id == clinic.id)
        existing_docs = (await session.execute(doc_stmt)).scalars().all()

        if not existing_docs:
            doc1 = Doctor(
                clinic_id=clinic.id,
                name="Dr. Rajesh Varma",
                specialization="Panchakarma & Pulse Diagnosis Specialist",
                consultation_fee=Decimal("600.00"),
                bio="BAMS, MD (Ayurveda) with 18+ years experience in authentic Kerala Panchakarma therapies.",
                is_active=True
            )
            doc2 = Doctor(
                clinic_id=clinic.id,
                name="Dr. Ananya Nair",
                specialization="Ayurvedic Dietetics & Skin Wellness",
                consultation_fee=Decimal("500.00"),
                bio="Expert in herbal pharmacology and holistic lifestyle coaching.",
                is_active=True
            )
            session.add_all([doc1, doc2])
            await session.flush()

            # Create Schedules: Monday - Saturday
            for day in range(6):
                session.add(DoctorSchedule(
                    doctor_id=doc1.id,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    slot_duration_minutes=30,
                    is_active=True
                ))
                session.add(DoctorSchedule(
                    doctor_id=doc2.id,
                    day_of_week=day,
                    start_time=time(10, 0),
                    end_time=time(18, 0),
                    slot_duration_minutes=30,
                    is_active=True
                ))
            await session.flush()
            existing_docs = [doc1, doc2]

        doc1 = existing_docs[0]
        doc2 = existing_docs[1] if len(existing_docs) > 1 else existing_docs[0]

        now = datetime.now(timezone.utc)

        # 4. Create Sample Appointments
        appointments_data = [
            {
                "patient_name": "Kavita Raman",
                "patient_phone": "+91 98765 43210",
                "patient_email": "kavita.raman@example.com",
                "doctor": doc1,
                "time": now + timedelta(hours=3),
                "status": AppointmentStatus.BOOKED,
                "treatment": "Panchakarma Consultation",
                "notes": "Patient reports severe cervical stiffness and fatigue.",
                "transcript": (
                    "Agent: Namaste! Welcome to Sree Kerala Ayurvedic Clinic. How may I assist you today?\n"
                    "Patient: Hello, I have severe neck stiffness and want to consult Dr. Varma for Panchakarma.\n"
                    "Agent: Dr. Rajesh Varma specializes in Panchakarma therapies. He has an open slot at 11:30 AM today. Shall I book that for you?\n"
                    "Patient: Yes please, my name is Kavita Raman, phone number is +91 98765 43210.\n"
                    "Agent: Perfect, your appointment is confirmed for 11:30 AM. Your confirmation ID is AYUR-5821. See you soon!"
                )
            },
            {
                "patient_name": "Arjun Menon",
                "patient_phone": "+91 97456 78901",
                "patient_email": "arjun.m@example.com",
                "doctor": doc2,
                "time": now + timedelta(days=1, hours=2),
                "status": AppointmentStatus.BOOKED,
                "treatment": "Dosha Assessment & Diet Plan",
                "notes": "Inquiry regarding hyperacidity and Pitta dosha balancing.",
                "transcript": (
                    "Agent: Namaste! Welcome to Sree Kerala Ayurvedic Clinic.\n"
                    "Patient: Hi, I've had continuous indigestion and acid reflux. Can I get a personalized diet consultation?\n"
                    "Agent: Dr. Ananya Nair is our specialist in Ayurvedic dietetics. She is available tomorrow at 02:00 PM. Would that work for you?\n"
                    "Patient: Yes, 2:00 PM tomorrow is great. My name is Arjun Menon.\n"
                    "Agent: Excellent, Arjun. Your consultation is reserved under booking reference AYUR-7392."
                )
            },
            {
                "patient_name": "Meera Pillai",
                "patient_phone": "+91 94471 23456",
                "patient_email": "meera.pillai@example.com",
                "doctor": doc1,
                "time": now - timedelta(days=1, hours=4),
                "status": AppointmentStatus.COMPLETED,
                "treatment": "Nadi Pariksha & Pulse Diagnosis",
                "notes": "Completed initial pulse assessment; prescribed herbal decoctions and dietary changes.",
                "transcript": (
                    "Agent: Namaste! Welcome to Sree Kerala Ayurvedic Clinic.\n"
                    "Patient: I want to book a pulse diagnosis session with Dr. Varma.\n"
                    "Agent: Dr. Varma has a slot available at 10:00 AM yesterday. Confirmed under booking ID AYUR-3104."
                )
            },
            {
                "patient_name": "Sunil Kumar",
                "patient_phone": "+91 98460 55555",
                "patient_email": "sunil.k@example.com",
                "doctor": doc2,
                "time": now + timedelta(days=2, hours=5),
                "status": AppointmentStatus.BOOKED,
                "treatment": "Ayurvedic Skin Wellness Therapy",
                "notes": "Patient seeking herbal remedies for chronic eczema.",
                "transcript": (
                    "Agent: Namaste! Welcome to Sree Kerala Ayurvedic Clinic.\n"
                    "Patient: Hello, do you treat skin conditions with Ayurveda?\n"
                    "Agent: Yes! Dr. Ananya Nair specializes in herbal dermatological wellness. Would you like an appointment on Thursday?\n"
                    "Patient: Yes please, book me for Thursday at 03:00 PM under Sunil Kumar.\n"
                    "Agent: Your booking is confirmed with ID AYUR-9021."
                )
            }
        ]

        for item in appointments_data:
            app = Appointment(
                clinic_id=clinic.id,
                doctor_id=item["doctor"].id,
                patient_name=item["patient_name"],
                patient_phone=item["patient_phone"],
                patient_email=item["patient_email"],
                appointment_time=item["time"],
                status=item["status"],
                treatment_type=item["treatment"],
                notes=item["notes"],
                call_transcript=item["transcript"]
            )
            session.add(app)
            await session.flush()

            # Add corresponding CallLog
            call_log = CallLog(
                clinic_id=clinic.id,
                call_sid=f"CA_{uuid.uuid4().hex[:12].upper()}",
                caller_phone=item["patient_phone"],
                duration_seconds=135,
                recording_url=f"https://api.elevenlabs.io/recordings/{uuid.uuid4().hex[:8]}.mp3",
                transcript=item["transcript"],
                summary=f"Patient {item['patient_name']} scheduled {item['treatment']} with {item['doctor'].name}.",
                sentiment="positive",
                outcome="appointment_booked",
                appointment_id=app.id
            )
            session.add(call_log)

        # 5. General Inquiry Call Logs (No booking)
        general_calls = [
            {
                "phone": "+91 98112 33445",
                "duration": 65,
                "sentiment": "neutral",
                "outcome": "inquiry_answered",
                "summary": "Caller inquired about clinic opening hours, consultation fees, and parking facilities.",
                "transcript": (
                    "Agent: Namaste! Welcome to Sree Kerala Ayurvedic Clinic. How can I help you?\n"
                    "Caller: Hello, could you tell me your operating hours and where you are located?\n"
                    "Agent: We are located at 108 Dhanwantari Road, Fort Kochi. We are open Monday through Saturday from 9:00 AM to 6:00 PM.\n"
                    "Caller: Thank you very much, that's very helpful!"
                )
            },
            {
                "phone": "+91 99001 22334",
                "duration": 92,
                "sentiment": "positive",
                "outcome": "inquiry_answered",
                "summary": "Caller asked about authentic 7-day Panchakarma detoxification packages and accommodation.",
                "transcript": (
                    "Agent: Namaste! Sree Kerala Ayurvedic Clinic. How may I assist you today?\n"
                    "Caller: Hi! Do you offer inpatient accommodation for residential Panchakarma detox programs?\n"
                    "Agent: Yes, we provide both outpatient therapies and traditional residential Panchakarma packages. You can book an initial consultation with Dr. Rajesh Varma to determine your personalized treatment plan.\n"
                    "Caller: Great, I will call back tomorrow with my travel dates. Thank you!"
                )
            }
        ]

        for gc in general_calls:
            session.add(CallLog(
                clinic_id=clinic.id,
                call_sid=f"CA_{uuid.uuid4().hex[:12].upper()}",
                caller_phone=gc["phone"],
                duration_seconds=gc["duration"],
                recording_url=f"https://api.elevenlabs.io/recordings/{uuid.uuid4().hex[:8]}.mp3",
                transcript=gc["transcript"],
                summary=gc["summary"],
                sentiment=gc["sentiment"],
                outcome=gc["outcome"]
            ))

        await session.commit()
        print("✓ Successfully seeded rich clinical appointments and call logs!")


if __name__ == "__main__":
    asyncio.run(seed_rich_data())

