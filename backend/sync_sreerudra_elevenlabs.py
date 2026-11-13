"""Sync Sreerudra Ayurveda Multi Speciality Hospital Knowledge Base directly to ElevenLabs Agent."""

import json
import os
import sys
from pathlib import Path
import urllib.request
import urllib.error

WORKSPACE_ROOT = str(Path(__file__).resolve().parent.parent)
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from backend.app.core.elevenlabs_config import (
    DEFAULT_FIRST_MESSAGE,
    DEFAULT_MALAYALAM_VOICE_ID,
    DEFAULT_TTS_MODEL_ID,
    build_elevenlabs_agent_patch,
    build_receptionist_system_prompt,
)


def _load_env_value(key: str, default: str = "") -> str:
    if os.getenv(key):
        return os.environ[key]
    for env_path in (
        Path(__file__).resolve().parent / ".env",
        Path(__file__).resolve().parent.parent / ".env",
    ):
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == key:
                    return v.strip().strip('"').strip("'")
    return default


ELEVENLABS_API_KEY = _load_env_value("ELEVENLABS_API_KEY")
AGENT_ID = _load_env_value("ELEVENLABS_AGENT_ID", "agent_0901m79nh3fcfhj9yn7f6ktqggfx")
VOICE_ID = _load_env_value("ELEVENLABS_VOICE_ID", DEFAULT_MALAYALAM_VOICE_ID)
TTS_MODEL_ID = _load_env_value("ELEVENLABS_TTS_MODEL_ID", DEFAULT_TTS_MODEL_ID)

SREERUDRA_KNOWLEDGE_BASE = """# Legacy & Heritage
You represent a 20+ year legacy of authentic Kerala Ayurvedic excellence, rooted in the revered Kudalmana family lineage.

# Hospital Identity & Branches
- Legal Name: Sreerudra Ayurveda Multi Speciality Hospital Research Centre (ശ്രീരുദ്ര ആയുർവേദ മൾട്ടി സ്പെഷ്യാലിറ്റി ഹോസ്പിറ്റൽ റിസർച്ച് സെന്റർ)
- Founded in 2002. NABH-Accredited multi-speciality hospital with In-Patient (IPD) and Out-Patient (OPD) facilities.
- Main Campus (Alappuzha): Kaithavana, Alappuzha, Kerala – 688003 (behind Kaithavana Church, tranquil lakeside setting). Phones: +91 477 2266778 / +91 98479 48218.
- Trivandrum Campus: Kallampally, Sreekariyam, Thiruvananthapuram, Kerala – 695017. Phones: +91 471 2590045 / +91 95677 48218.
- Consultation Hubs: Kochi (Ernakulam).
- Central Helpline: +91 90379 03333
- Website: https://www.sreerudraayurveda.com | Email: info@sreerudraayurveda.com

# Medical Leadership, Specialist Doctors & Consultation Timings
1. Dr. K. S. Vishnu Nampoothiry - Founder, Patron & Medical Director (BAMS, MD Ayurveda, PGDYT, MSc Yoga). Senior Medical Officer (Alappuzha), AMAI State President. Timings: Mon-Fri, 9:00 AM - 2:00 PM (Fee: ₹750). Key specializations: Ayurvedic Oncology (Cancer supportive care), Classical Panchakarma, Neurological rehabilitation (Stroke, Paralysis, Parkinson's), and severe Spine & Musculoskeletal disorders. Prior appointment mandatory!
2. Dr. Maya Lakshmi Vishnu Nampoothiry - Managing Director (Hospital Administration & patient care systems). Timings: Mon-Sat, 9:00 AM - 5:00 PM.
3. Dr. Rabith K. Rajan - Chief Physician (BAMS, PGDYT). Timings: Mon-Sat, 9:00 AM - 5:00 PM (Fee: ₹500). General Ayurvedic Medicine, Panchakarma, Yoga therapy, In-Patient care.
4. Dr. Amritha R. S. - Senior Consultant (MS Ayurveda). Timings: Mon-Sat, 10:00 AM - 4:00 PM (Fee: ₹500). Proctology (Anorectal) & Orthopaedics, joint diseases, arthritis, spine.
5. Dr. Reshma Paul - Consultant (BAMS). Timings: Mon, Wed, Fri, Sat, 10:00 AM - 4:00 PM (Fee: ₹450). Siddha & Ayurvedic Medicine, Dermatology (Psoriasis, Eczema, Vitiligo).
6. Dr. Muhammed Hashim A. P. - Consultant Proctologist (BAMS, PGD Kshara Karma). Timings: Tue-Sat, 9:30 AM - 4:30 PM (Fee: ₹500). Specialist in Ksharasoothra and Kshara Karma for Anal Fistula, Fissure, Pilonidal Sinus, and Piles (Hemorrhoids).
7. Dr. Abdul Rasheed - Senior Consultant (Rtd. Joint Director ISM). Timings: Mon-Fri, 9:00 AM - 1:00 PM (Fee: ₹500). General Medicine, Geriatric healthcare, Metabolic & lifestyle diseases.

# Clinical Specialties & Treatments
- Ayurvedic Oncology: Physician-led cancer supportive care under Dr. Vishnu Nampoothiry to enhance immunity (Ojas), reduce chemo/radiation side-effects, manage pain, and assist recovery.
- Spine & Orthopaedics: Low back pain, Cervical Spondylosis, Slip disc, Sciatica, Osteoarthritis, Rheumatoid arthritis, Frozen shoulder. Procedures: Kati Vasti, Greeva Vasti, Janu Vasti, Elakizhi, Podikizhi, Pizhichil.
- Neurology & Stroke Rehab: Paralysis rehabilitation, Parkinson's, Multiple Sclerosis, Migraine, Insomnia, Anxiety/Depression. Procedures: Shirodhara, Shirovasti, Nasyam, Medhya Rasayanas.
- Pediatrics & Autism: Holistic management for Autism Spectrum Disorder (ASD) and developmental delays.
- Proctology (Ksharasoothra): Non-surgical / minimally invasive Ksharasoothra medicated thread therapy for Anal Fistula and Piles with very low recurrence.
- Dermatology: Psoriasis, Eczema, Vitiligo, skin allergies, natural Ayurvedic hair & skin care.
- Metabolic & Lifestyle: Obesity (Udvartanam herbal powder massage), Diabetes, Hypertension, Cholesterol, Fatty Liver.
- Women's Health: PCOD/PCOS, Fibroids, Infertility, Post-Natal Care (Prasava Raksha 28/45-day package).
- Classical Panchakarma: Vamana, Virechana, Vasti, Nasya, Raktamokshana, Abhyangam, Shirodhara, Pizhichil, Njavarakizhi.
- In-Patient (IPD) Facilities: Hygienic private and shared recovery rooms, customized Ayurvedic diet (Pathya Ahara) prepared in-house, round-the-clock nursing. We welcome outstation and international patients (from USA, UK, UAE, Europe) with 7, 14, 21, or 28-day packages."""

SREERUDRA_PROMPT = build_receptionist_system_prompt(
    clinic_name="Sreerudra Ayurveda Multi Speciality Hospital Research Centre",
    knowledge_base=SREERUDRA_KNOWLEDGE_BASE,
)

FIRST_MESSAGE = DEFAULT_FIRST_MESSAGE

TOOL_IDS = [
    "tool_8801m79n5dhvezj96qxf25yea1vh",  # check_availability
    "tool_3901m79n5ebxf76806ex6qknwtkq",  # book_appointment
    "tool_7201m79n5fbkfm1ag59jx6exvpwt",  # find_appointment
    "tool_0501m79n5g86fj2v88t249g5y2yy",  # reschedule_appointment
    "tool_6601m79n5h46fxr98bw12xqxtfm6",  # cancel_appointment
    "tool_2601m79n5j5mfh3atbfzwk0kxbrh",  # escalate_to_staff
]

def update_agent():
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY is not set in environment or .env")
    url = f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}"
    
    payload = build_elevenlabs_agent_patch(
        prompt=SREERUDRA_PROMPT,
        voice_id=VOICE_ID,
        model_id=TTS_MODEL_ID,
        tool_ids=TOOL_IDS,
        first_message=FIRST_MESSAGE,
        disable_first_message_interruptions=False,
        agent_name="Asha - Sreerudra Ayurveda AI Receptionist",
    )

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        method="PATCH"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            print("SUCCESS! ElevenLabs Agent updated successfully.")
            print(f"Agent Name: {data.get('name')}")
            print(f"First Message: {data.get('conversation_config', {}).get('agent', {}).get('first_message')}")
            return True
    except urllib.error.HTTPError as e:
        print(f"HTTPError {e.code}: {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    update_agent()

