"""Direct SQLite & PostgreSQL Seeder for Sreerudra Ayurveda Multi Speciality Hospital Research Centre."""

import sqlite3
import uuid
from datetime import datetime, timezone

SREERUDRA_KB = """================================================================================
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

3. MEDICAL LEADERSHIP & DOCTORS TEAM
1. Dr. K. S. Vishnu Nampoothiry
- Designation: Founder, Chairman, Patron & Medical Director
- Qualifications: BAMS, MD (Ayurveda), PGDYT, MSc Yoga
- Credentials: Kudalmana Ayurvedic lineage, 20+ years clinical experience, Senior Medical Officer (Alappuzha), AMAI State President.
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
5. Preferred Branch: Alappuzha, Trivandrum, or Kochi Clinic
6. Mode: In-Person OPD Visit, In-Patient (IPD) Stay, or Video Tele-Consultation
7. Preferred Date & Time
"""

DOCTORS = [
    (
        "Dr. K. S. Vishnu Nampoothiry",
        "Medical Director - Ayurvedic Oncology, Panchakarma & Spine",
        750.00,
        "BAMS, MD (Ayurveda), PGDYT, MSc Yoga. 20+ yrs clinical experience, Senior Medical Officer (Alappuzha), AMAI State President. Expert in Cancer supportive care, Classical Panchakarma, Stroke rehab, and severe Spine disorders.",
        [0, 1, 2, 3, 4],
        ("09:00:00", "14:00:00")
    ),
    (
        "Dr. Rabith K. Rajan",
        "Chief Physician - General Medicine & Panchakarma",
        500.00,
        "BAMS, PGDYT. Chief Physician specializing in holistic internal medicine, Panchakarma therapies, and clinical inpatient management.",
        [0, 1, 2, 3, 4, 5],
        ("09:00:00", "17:00:00")
    ),
    (
        "Dr. Amritha R. S.",
        "Senior Consultant - Proctology & Orthopaedics",
        500.00,
        "MS (Ayurveda). Specialist in Ayurvedic proctology (anorectal disorders) and orthopaedic joint diseases, spine disorders, and arthritis.",
        [0, 1, 2, 3, 4, 5],
        ("10:00:00", "16:00:00")
    ),
    (
        "Dr. Reshma Paul",
        "Consultant - Dermatology & Siddha Medicine",
        450.00,
        "BAMS. Expert in dermatology (Psoriasis, Eczema, Vitiligo), systemic herbal medicine, and integration of classical Siddha therapies.",
        [0, 2, 4, 5],
        ("10:00:00", "16:00:00")
    ),
    (
        "Dr. Muhammed Hashim A. P.",
        "Consultant Proctologist - Ksharasoothra Specialist",
        500.00,
        "BAMS, PGD Kshara Karma. Specialist in Ksharasoothra and Kshara Karma treatments for Anal Fistula, Fissure, Pilonidal Sinus, and Piles.",
        [1, 2, 3, 4, 5],
        ("09:30:00", "16:30:00")
    ),
    (
        "Dr. Abdul Rasheed",
        "Senior Consultant - General Medicine & Geriatrics",
        500.00,
        "Rtd. Joint Director, ISM. Decades of clinical expertise in general medicine, geriatric wellness, and chronic metabolic lifestyle diseases.",
        [0, 1, 2, 3, 4],
        ("09:00:00", "13:00:00")
    ),
    (
        "Dr. Maya Lakshmi Vishnu Nampoothiry",
        "Managing Director - Hospital Administration",
        0.00,
        "M.Sc, MBA, B.Ed, Ph.D. Managing Director overseeing hospital administration, patient-centered care systems, and clinical quality.",
        [0, 1, 2, 3, 4, 5],
        ("09:00:00", "17:00:00")
    ),
]


def seed_sqlite(db_path="ayurvoice.db"):
    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    now_str = datetime.now(timezone.utc).isoformat()

    # 1. Update primary clinic
    row = cur.execute("SELECT id FROM clinics LIMIT 1").fetchone()
    if row:
        clinic_id = row[0]
        cur.execute("""
            UPDATE clinics 
            SET name = ?, slug = ?, phone_number = ?, address = ?, knowledge_base = ?, updated_at = ?
            WHERE id = ?
        """, (
            "Sreerudra Ayurveda Multi Speciality Hospital Research Centre",
            "sreerudra-ayurveda",
            "+919037903333",
            "Kaithavana, Alappuzha & Kallampally, Sreekariyam, Trivandrum, Kerala",
            SREERUDRA_KB,
            now_str,
            clinic_id
        ))
        print(f"Updated Clinic {clinic_id}")
    else:
        clinic_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO clinics (id, name, slug, phone_number, address, timezone, created_at, updated_at, knowledge_base)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            clinic_id,
            "Sreerudra Ayurveda Multi Speciality Hospital Research Centre",
            "sreerudra-ayurveda",
            "+919037903333",
            "Kaithavana, Alappuzha & Kallampally, Sreekariyam, Trivandrum, Kerala",
            "Asia/Kolkata",
            now_str,
            now_str,
            SREERUDRA_KB
        ))
        print(f"Created Clinic {clinic_id}")

    # 2. Update Admin user if exists
    cur.execute("""
        UPDATE users 
        SET full_name = 'Dr. K. S. Vishnu Nampoothiry', email = 'admin@sreerudraayurveda.com'
        WHERE clinic_id = ?
    """, (clinic_id,))

    # 3. Clean up older doctors and schedules
    cur.execute("DELETE FROM doctor_schedules WHERE doctor_id IN (SELECT id FROM doctors WHERE clinic_id = ?)", (clinic_id,))
    cur.execute("DELETE FROM doctors WHERE clinic_id = ?", (clinic_id,))

    # 4. Insert all 7 Sreerudra doctors and weekly schedules
    for doc_name, spec, fee, bio, days, (st, et) in DOCTORS:
        doc_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO doctors (id, clinic_id, name, specialization, consultation_fee, bio, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
        """, (doc_id, clinic_id, doc_name, spec, fee, bio, now_str, now_str))
        print(f"  + Added doctor: {doc_name}")

        for day in days:
            sched_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO doctor_schedules (id, doctor_id, day_of_week, start_time, end_time, slot_duration_minutes, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 30, 1, ?, ?)
            """, (sched_id, doc_id, day, st, et, now_str, now_str))

    conn.commit()
    conn.close()
    print("SUCCESS: Local SQLite Database updated with Sreerudra Ayurveda!")


if __name__ == "__main__":
    seed_sqlite()

