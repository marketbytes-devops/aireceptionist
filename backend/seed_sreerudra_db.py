"""Seed Sreerudra Ayurveda Multi Speciality Hospital Research Centre
Updates the primary clinic, creates the 7 doctors, registers weekly schedules, and syncs knowledge base.
"""

import asyncio
import uuid
from decimal import Decimal
from datetime import time
from sqlalchemy import select, delete
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.core.security import get_password_hash
from backend.app.models.clinic import Clinic
from backend.app.models.doctor import Doctor
from backend.app.models.schedule import DoctorSchedule
from backend.app.models.appointment import Appointment, AppointmentStatus
from backend.app.models.call_log import CallLog
from backend.app.models.user import User, UserRole

SREERUDRA_KB_TEXT = """================================================================================
🏥 SREERUDRA AYURVEDA MULTI SPECIALITY HOSPITAL RESEARCH CENTRE
ശ്രീരുദ്ര ആയുർവേദ മൾട്ടി സ്പെഷ്യാലിറ്റി ഹോസ്പിറ്റൽ റിസർച്ച് സെന്റർ
MASTER HOSPITAL KNOWLEDGE BASE & CLINICAL DIRECTORY
================================================================================

1. EXECUTIVE SUMMARY & IDENTITY
- Official Legal Name: Sreerudra Ayurveda Multi Speciality Hospital Research Centre
- Short Name: Sreerudra Ayurveda
- Founded In: 2002 (over 20+ years of clinical service)
- Accreditation: NABH-Accredited (National Accreditation Board for Hospitals & Healthcare Providers)
- Heritage & Lineage: Rooted in the celebrated Kudalmana family tradition of Kerala, historically renowned for Ayurveda, Vedic scholarship, Sanskrit treatises, and traditional healing systems.
- Healing Philosophy: Seamless integration of classical Kerala Ayurveda, authentic Panchakarma, and Yoga therapy with modern medical diagnostic investigations. Treatments target the root cause of diseases by restoring the balance of the Tridoshas (Vata, Pitta, Kapha) and enhancing Ojas (vital energy).
- Patients Served: 5,000+ satisfied domestic and international patients (from USA, UK, UAE, Singapore, Europe, etc.).
- Official Website: https://www.sreerudraayurveda.com
- Official Email: info@sreerudraayurveda.com / email@sreerudraayurveda.com
- Central Helpline / Phone: +91 90379 03333

2. HOSPITAL BRANCHES & CONTACT DIRECTORY
📍 Branch 1: Alappuzha (Alleppey) — Main Hospital Campus & Research Centre
- Address: Sreerudra Ayurveda Multi-Speciality Hospital, Kaithavana, Alappuzha, Kerala – 688003, India.
- Landmark: Located behind Kaithavana Church (peaceful lakeside setting, 10 mins drive from Alappuzha town center & railway station).
- Landline Phone: +91 477 2266778 | Mobile / WhatsApp: +91 98479 48218
- Facilities: Full In-Patient (IPD) wards, peaceful recovery rooms, specialized Panchakarma therapy suites, in-house customized Ayurvedic diet kitchen, round-the-clock nursing.

📍 Branch 2: Thiruvananthapuram (Trivandrum) — Hospital Campus
- Address: Sreerudra Ayurveda Multi-Speciality Hospital, Kallampally, Sreekariyam, Thiruvananthapuram (Trivandrum), Kerala – 695017, India.
- Landmark: Kallampally, Sreekariyam (accessible via public transport, railway station, & Trivandrum International Airport).
- Landline Phone: +91 471 2590045 | Mobile / WhatsApp: +91 95677 48218
- Facilities: Full In-Patient (IPD) & Out-Patient (OPD) care, therapy suites, doctor consultation chambers.

📍 Clinical Consultation & Regional Hubs:
- Kochi (Ernakulam): Dedicated Ayurvedic consultation clinic catering to patients from Kakkanad, Edappally, Aluva, Vyttila, and Tripunithura.
- Kottayam: Consultation and referral access serving patients from Changanassery, Pala, Ettumanoor, Vaikom, and Kumarakom.

3. MEDICAL LEADERSHIP & DOCTORS TEAM
1. Dr. K. S. Vishnu Nampoothiry
- Designation: Founder, Chairman, Patron & Medical Director
- Qualifications: BAMS, MD (Ayurveda), PGDYT, MSc Yoga
- Credentials: Kudalmana Ayurvedic lineage, 20+ years experience, Senior Medical Officer (Alappuzha), AMAI State President.
- Specializations: Ayurvedic Oncology (Cancer Supportive Care), Classical Panchakarma, Neurological Rehabilitation & Stroke Recovery, Severe Spine & Musculoskeletal disorders. Prior appointment mandatory!
- Consultation Fee: ₹750

2. Dr. Maya Lakshmi Vishnu Nampoothiry
- Designation: Managing Director
- Qualifications: M.Sc, MBA, B.Ed, Ph.D
- Role: Hospital administration, patient-centered care systems, treatment coordination.

3. Dr. Rabith K. Rajan
- Designation: Chief Physician
- Qualifications: BAMS, PGDYT
- Specializations: General Ayurvedic Medicine, Panchakarma therapy, Yoga therapy, In-Patient clinical management.
- Consultation Fee: ₹500

4. Dr. Amritha R. S.
- Designation: Senior Consultant – Proctology & Orthopaedics
- Qualifications: MS (Ayurveda)
- Specializations: Ayurvedic Proctology (Anorectal disorders), Orthopaedic care, Joint diseases, Arthritis, Spine disorders.
- Consultation Fee: ₹500

5. Dr. Reshma Paul
- Designation: Consultant – Siddha & Ayurvedic Medicine
- Qualifications: BAMS
- Specializations: Dermatology (Psoriasis, Eczema, Vitiligo), Systemic herbal medicine, Siddha integration.
- Consultation Fee: ₹450

6. Dr. Muhammed Hashim A. P.
- Designation: Consultant Proctologist (Ksharasoothra Specialist)
- Qualifications: BAMS, PGD Kshara Karma
- Specializations: Ksharasoothra and Kshara Karma treatments for Anal Fistula, Anal Fissure, Pilonidal Sinus, and Hemorrhoids/Piles.
- Consultation Fee: ₹500

7. Dr. Abdul Rasheed
- Designation: Senior Consultant – General Medicine
- Qualifications: Rtd. Joint Director, ISM (Indian Systems of Medicine)
- Specializations: Comprehensive internal medicine, Geriatric healthcare, Metabolic & lifestyle disorders.
- Consultation Fee: ₹500

4. CLINICAL SPECIALTIES & TREATMENTS
🧬 1. Ayurvedic Oncology (Cancer Supportive Care)
- Physician-led integrative care under Dr. K. S. Vishnu Nampoothiry.
- Improves quality of life, maintains Ojas/immunity, reduces chemo/radiation side effects, alleviates fatigue/pain.
- Cancers managed: Breast, prostate, thyroid, gastrointestinal, lung, and testicular cancers.

🦴 2. Spine, Joint & Orthopaedic Care
- Conditions: Low back pain, Cervical Spondylosis, Slip Disc, Spinal Stenosis, Sciatica, Osteoarthritis, Ankylosing Spondylitis, Rheumatoid Arthritis, Gout, Frozen Shoulder.
- Key Procedures: Kati Vasti, Greeva Vasti, Janu Vasti, Elakizhi, Podikizhi, Pizhichil, Lepanam.

🧠 3. Neurology, Stroke Rehab & Mental Health
- Conditions: Post-stroke paralysis rehab, Parkinson's Disease, Multiple Sclerosis (MS), Dementia, Trigeminal Neuralgia, Migraine, Vertigo, Insomnia, Stress, Anxiety & Depression.
- Procedures: Shirodhara, Shirovasti, Nasyam, Medhya Rasayanas, Yoga & Pranayama.

👶 4. Pediatrics & Neurodevelopmental Care (Autism)
- Holistic management for Autism Spectrum Disorder (ASD) and developmental delays using Medhya Ghritas, Nasya, Shirodhara, and Yoga therapy.

🩺 5. Proctology & Anorectal Clinic (Ksharasoothra)
- Classical non-surgical Ksharasoothra (medicated thread) therapy for Anal Fistula, Fissure, Pilonidal Sinus, and Piles with very low recurrence.

🌿 6. Dermatology & Cosmetology
- Psoriasis, Eczema, Vitiligo, Urticaria, Lipoma, Allergic Dermatitis, Hair fall treatments, anti-pigmentation skin care.

🩸 7. Metabolic & Lifestyle Disorders
- Weight loss / Obesity management (Udvartanam), Diabetes Mellitus, Hypertension, High Cholesterol, Thyroid disorders, Fatty Liver.

🌸 8. Women's Health (Gynecology & Obstetrics)
- PCOD/PCOS, Fibroids, Infertility, Post-Natal Care (Prasava Raksha - 28/45-day mother & newborn recovery).

🍃 9. Classical Panchakarma & Rejuvenation
- 5 Detox Therapies: Vamana, Virechana, Vasti/Basti, Nasya, Raktamokshana.
- Wellness packages: Abhyanga, Shirodhara, Pizhichil, Njavarakizhi, Kayakalpa anti-aging.

5. IN-PATIENT (IPD) FACILITIES & PATIENT CARE
- Accommodation: Clean, ventilated private and shared recovery rooms in peaceful lakeside (Alappuzha) and tranquil (Trivandrum) campuses.
- Customized Diet (Pathya Ahara): Wholesome vegetarian meals planned for each patient according to disease, digestive Agni, and Tridosha balance.
- International & Outstation Support: Airport transfers, pre-arrival tele-consultation, customized packages (7, 14, 21, or 28 days).

6. PATIENT BOOKING INFORMATION
Required fields collected for booking:
1. Patient Full Name
2. Phone / WhatsApp Number
3. Current City / Location
4. Health Complaint / Treatment Required
5. Preferred Branch: Alappuzha, Trivandrum, or Kochi/Kottayam Clinic
6. Mode: In-Person OPD Visit, In-Patient (IPD) Stay, or Video Tele-Consultation
7. Preferred Date & Time
"""

DOCTORS_DATA = [
    {
        "name": "Dr. K. S. Vishnu Nampoothiry",
        "specialization": "Medical Director - Ayurvedic Oncology, Panchakarma & Spine",
        "fee": Decimal("750.00"),
        "bio": "BAMS, MD (Ayurveda), PGDYT, MSc Yoga. 20+ yrs clinical experience, Senior Medical Officer (Alappuzha), AMAI State President. Expert in Cancer supportive care, Classical Panchakarma, Stroke rehab, and severe Spine disorders.",
        "days": [0, 1, 2, 3, 4],  # Mon-Fri
        "hours": (time(9, 0), time(14, 0))
    },
    {
        "name": "Dr. Rabith K. Rajan",
        "specialization": "Chief Physician - General Medicine & Panchakarma",
        "fee": Decimal("500.00"),
        "bio": "BAMS, PGDYT. Chief Physician specializing in holistic internal medicine, Panchakarma therapies, and clinical inpatient management.",
        "days": [0, 1, 2, 3, 4, 5],  # Mon-Sat
        "hours": (time(9, 0), time(17, 0))
    },
    {
        "name": "Dr. Amritha R. S.",
        "specialization": "Senior Consultant - Proctology & Orthopaedics",
        "fee": Decimal("500.00"),
        "bio": "MS (Ayurveda). Specialist in Ayurvedic proctology (anorectal disorders) and orthopaedic joint diseases, spine disorders, and arthritis.",
        "days": [0, 1, 2, 3, 4, 5],
        "hours": (time(10, 0), time(16, 0))
    },
    {
        "name": "Dr. Reshma Paul",
        "specialization": "Consultant - Dermatology & Siddha Medicine",
        "fee": Decimal("450.00"),
        "bio": "BAMS. Expert in dermatology (Psoriasis, Eczema, Vitiligo), systemic herbal medicine, and integration of classical Siddha therapies.",
        "days": [0, 2, 4, 5],  # Mon, Wed, Fri, Sat
        "hours": (time(10, 0), time(16, 0))
    },
    {
        "name": "Dr. Muhammed Hashim A. P.",
        "specialization": "Consultant Proctologist - Ksharasoothra Specialist",
        "fee": Decimal("500.00"),
        "bio": "BAMS, PGD Kshara Karma. Specialist in Ksharasoothra and Kshara Karma treatments for Anal Fistula, Fissure, Pilonidal Sinus, and Piles.",
        "days": [1, 2, 3, 4, 5],  # Tue-Sat
        "hours": (time(9, 30), time(16, 30))
    },
    {
        "name": "Dr. Abdul Rasheed",
        "specialization": "Senior Consultant - General Medicine & Geriatrics",
        "fee": Decimal("500.00"),
        "bio": "Rtd. Joint Director, ISM. Decades of clinical expertise in general medicine, geriatric wellness, and chronic metabolic lifestyle diseases.",
        "days": [0, 1, 2, 3, 4],
        "hours": (time(9, 0), time(13, 0))
    },
    {
        "name": "Dr. Maya Lakshmi Vishnu Nampoothiry",
        "specialization": "Managing Director - Hospital Administration",
        "fee": Decimal("0.00"),
        "bio": "M.Sc, MBA, B.Ed, Ph.D. Managing Director overseeing hospital administration, patient-centered care systems, and clinical quality.",
        "days": [0, 1, 2, 3, 4, 5],
        "hours": (time(9, 0), time(17, 0))
    }
]


async def seed_sreerudra():
    print("🏥 Starting Sreerudra Ayurveda Master Knowledge Base Seeding...")
    await init_db()

    async with AsyncSessionLocal() as session:
        # 1. Update or create Sreerudra Clinic
        clinic_stmt = select(Clinic).limit(1)
        res = await session.execute(clinic_stmt)
        clinic = res.scalar_one_or_none()

        if not clinic:
            clinic = Clinic(
                name="Sreerudra Ayurveda Multi Speciality Hospital Research Centre",
                slug="sreerudra-ayurveda",
                phone_number="+919037903333",
                address="Kaithavana, Alappuzha & Kallampally, Sreekariyam, Trivandrum, Kerala",
                timezone="Asia/Kolkata",
                knowledge_base=SREERUDRA_KB_TEXT
            )
            session.add(clinic)
        else:
            clinic.name = "Sreerudra Ayurveda Multi Speciality Hospital Research Centre"
            clinic.slug = "sreerudra-ayurveda"
            clinic.phone_number = "+919037903333"
            clinic.address = "Kaithavana, Alappuzha & Kallampally, Sreekariyam, Trivandrum, Kerala"
            clinic.timezone = "Asia/Kolkata"
            clinic.knowledge_base = SREERUDRA_KB_TEXT

        await session.commit()
        await session.refresh(clinic)
        print(f"✅ Clinic record updated: {clinic.name} (ID: {clinic.id})")

        # 2. Update Admin User
        user_stmt = select(User).where(User.clinic_id == clinic.id)
        admin_user = (await session.execute(user_stmt)).scalars().first()
        if admin_user:
            admin_user.full_name = "Dr. K. S. Vishnu Nampoothiry"
            admin_user.email = "admin@sreerudraayurveda.com"
        else:
            admin_user = User(
                email="admin@sreerudraayurveda.com",
                hashed_password=get_password_hash("Sreerudra2026!"),
                full_name="Dr. K. S. Vishnu Nampoothiry",
                role=UserRole.CLINIC_ADMIN,
                clinic_id=clinic.id,
                is_active=True
            )
            session.add(admin_user)
        await session.commit()

        # 3. Clean up older placeholder doctors & register the 7 Sreerudra doctors
        # Fetch existing doctors
        existing_doc_stmt = select(Doctor).where(Doctor.clinic_id == clinic.id)
        existing_docs = (await session.execute(existing_doc_stmt)).scalars().all()
        existing_doc_map = {d.name: d for d in existing_docs}

        for doc_info in DOCTORS_DATA:
            doc = existing_doc_map.get(doc_info["name"])
            if not doc:
                doc = Doctor(
                    clinic_id=clinic.id,
                    name=doc_info["name"],
                    specialization=doc_info["specialization"],
                    consultation_fee=doc_info["fee"],
                    bio=doc_info["bio"],
                    is_active=True
                )
                session.add(doc)
                await session.flush()
                print(f"  + Added doctor: {doc.name}")
            else:
                doc.specialization = doc_info["specialization"]
                doc.consultation_fee = doc_info["fee"]
                doc.bio = doc_info["bio"]
                doc.is_active = True
                print(f"  * Updated doctor: {doc.name}")

            # Delete old schedules and create new ones
            await session.execute(delete(DoctorSchedule).where(DoctorSchedule.doctor_id == doc.id))
            
            start_t, end_t = doc_info["hours"]
            for day in doc_info["days"]:
                sched = DoctorSchedule(
                    doctor_id=doc.id,
                    day_of_week=day,
                    start_time=start_t,
                    end_time=end_t,
                    slot_duration_minutes=30,
                    is_active=True
                )
                session.add(sched)

        await session.commit()
        print("✅ All 7 Sreerudra doctors and weekly schedules registered successfully!")

if __name__ == "__main__":
    asyncio.run(seed_sreerudra())

