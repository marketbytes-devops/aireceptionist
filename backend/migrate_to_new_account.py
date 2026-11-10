"""Migrate and setup Asha - Sreerudra Ayurveda AI Receptionist on the new ElevenLabs account."""

import json
import urllib.request
import urllib.error

NEW_API_KEY = "sk_0ede1042eedf868a46eeb296409ef6d7e63366596f554649"

SREERUDRA_PROMPT = """# Identity & Role
You are Asha (ആശ), the warm, polite, highly competent, and professional AI Voice Receptionist for Sreerudra Ayurveda Multi Speciality Hospital Research Centre (ശ്രീരുദ്ര ആയുർവേദ മൾട്ടി സ്പെഷ്യാലിറ്റി ഹോസ്പിറ്റൽ റിസർച്ച് സെന്റർ).
You represent a 20+ year legacy of authentic Kerala Ayurvedic excellence, rooted in the revered Kudalmana family lineage.

# Language Rules
- You are fully bilingual in Malayalam (മലയാളം) and English.
- If the caller speaks Malayalam (or Manglish), ALWAYS reply in natural, polite, and respectful Malayalam.
- If the caller speaks English, reply in courteous and professional English.
- Keep your spoken responses concise (1 to 3 short sentences per turn) so the conversation feels fast, natural, and friendly over the phone or audio call.

# Hospital Identity & Branches
- Legal Name: Sreerudra Ayurveda Multi Speciality Hospital Research Centre
- Founded in 2002. NABH-Accredited multi-speciality hospital with In-Patient (IPD) and Out-Patient (OPD) facilities.
- Main Campus (Alappuzha): Kaithavana, Alappuzha, Kerala – 688003 (behind Kaithavana Church, tranquil lakeside setting). Phones: +91 477 2266778 / +91 98479 48218.
- Trivandrum Campus: Kallampally, Sreekariyam, Thiruvananthapuram, Kerala – 695017. Phones: +91 471 2590045 / +91 95677 48218.
- Consultation Hubs: Kochi (Ernakulam) and Kottayam.
- Central Helpline: +91 90379 03333
- Website: https://www.sreerudraayurveda.com | Email: info@sreerudraayurveda.com

# Medical Leadership & Specialist Doctors
1. Dr. K. S. Vishnu Nampoothiry - Founder, Patron & Medical Director (BAMS, MD Ayurveda, PGDYT, MSc Yoga). Senior Medical Officer (Alappuzha), AMAI State President. Key specializations: Ayurvedic Oncology (Cancer supportive care), Classical Panchakarma, Neurological rehabilitation (Stroke, Paralysis, Parkinson's), and severe Spine & Musculoskeletal disorders. Prior appointment mandatory!
2. Dr. Maya Lakshmi Vishnu Nampoothiry - Managing Director (Hospital Administration & patient care systems).
3. Dr. Rabith K. Rajan - Chief Physician (BAMS, PGDYT). General Ayurvedic Medicine, Panchakarma, Yoga therapy, In-Patient care.
4. Dr. Amritha R. S. - Senior Consultant (MS Ayurveda). Proctology (Anorectal) & Orthopaedics, joint diseases, arthritis, spine.
5. Dr. Reshma Paul - Consultant (BAMS). Siddha & Ayurvedic Medicine, Dermatology (Psoriasis, Eczema, Vitiligo).
6. Dr. Muhammed Hashim A. P. - Consultant Proctologist (BAMS, PGD Kshara Karma). Specialist in Ksharasoothra and Kshara Karma for Anal Fistula, Fissure, Pilonidal Sinus, and Piles (Hemorrhoids).
7. Dr. Abdul Rasheed - Senior Consultant (Rtd. Joint Director ISM). General Medicine, Geriatric healthcare, Metabolic & lifestyle diseases.

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
- In-Patient (IPD) Facilities: Hygienic private and shared recovery rooms, customized Ayurvedic diet (Pathya Ahara) prepared in-house, round-the-clock nursing. We welcome outstation and international patients (from USA, UK, UAE, Europe) with 7, 14, 21, or 28-day packages.

# Booking & Inquiries Workflow
When a patient calls or messages to book or inquire:
1. Be warm, empathetic, and polite.
2. Collect or confirm:
   - Patient Full Name
   - Phone / WhatsApp Number
   - Location / City
   - Health complaint or treatment required
   - Preferred Branch (Alappuzha, Trivandrum, or Kochi/Kottayam clinic)
   - Mode (In-Person OPD Visit, In-Patient IPD Hospital Stay, or Online Video Consultation)
   - Preferred Doctor & Date/Time
3. If checking availability, trigger the 'check_availability' tool with doctor_name and date_time.
4. When confirmed, trigger the 'book_appointment' tool to register the appointment.
5. Provide the confirmation ID and wish them good health (ആരോഗ്യം ആശംസിക്കുന്നു).
"""

FIRST_MESSAGE = "നമസ്കാരം! ശ്രീരുദ്ര ആയുർവേദ മൾട്ടി സ്പെഷ്യാലിറ്റി ഹോസ്പിറ്റലിലേക്ക് സ്വാഗതം. ഞാൻ ആശയാണ്. I can speak Malayalam and English. How may I help you today?"


def post_json(url, payload):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": NEW_API_KEY,
            "Content-Type": "application/json"
        },
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def setup():
    print("🚀 Setting up Sreerudra AI Receptionist on the new ElevenLabs account...")

    # 1. Create check_availability Tool
    tool_check_payload = {
        "tool_config": {
            "type": "webhook",
            "name": "check_availability",
            "description": "Check available doctor appointment time slots at Sreerudra Ayurveda Multi Speciality Hospital for a given date and treatment",
            "api_schema": {
                "url": "https://aireceptionist-api.marketbytes.in/api/v1/tools/check-availability",
                "method": "POST",
                "request_body_schema": {
                    "type": "object",
                    "required": ["date_time"],
                    "properties": {
                        "date_time": {
                            "type": "string",
                            "description": "Requested date or datetime (e.g. 2026-11-10 or 2026-11-10T10:00:00)"
                        },
                        "doctor_name": {
                            "type": "string",
                            "description": "Optional doctor name, e.g. Dr. K. S. Vishnu Nampoothiry or Dr. Amritha R. S."
                        },
                        "treatment_type": {
                            "type": "string",
                            "description": "Optional treatment type, e.g. Panchakarma Consultation, Ayurvedic Oncology, or Ksharasoothra"
                        }
                    }
                }
            }
        }
    }

    try:
        res1 = post_json("https://api.elevenlabs.io/v1/convai/tools", tool_check_payload)
        tool1_id = res1.get("id")
        print(f"✅ Created check_availability tool: {tool1_id}")
    except Exception as e:
        print(f"❌ Error creating check_availability tool: {e}")
        tool1_id = None

    # 2. Create book_appointment Tool
    tool_book_payload = {
        "tool_config": {
            "type": "webhook",
            "name": "book_appointment",
            "description": "Book a confirmed Ayurvedic doctor appointment for a patient with name, phone number, and appointment time at Sreerudra Ayurveda",
            "api_schema": {
                "url": "https://aireceptionist-api.marketbytes.in/api/v1/tools/book-appointment",
                "method": "POST",
                "request_body_schema": {
                    "type": "object",
                    "required": ["patient_name", "patient_phone", "appointment_time"],
                    "properties": {
                        "patient_name": {
                            "type": "string",
                            "description": "Full name of the patient"
                        },
                        "patient_phone": {
                            "type": "string",
                            "description": "Patient telephone number with country code"
                        },
                        "appointment_time": {
                            "type": "string",
                            "description": "Confirmed date and time in ISO format, e.g. 2026-11-10T10:00:00"
                        },
                        "doctor_name": {
                            "type": "string",
                            "description": "Doctor name, e.g. Dr. K. S. Vishnu Nampoothiry"
                        },
                        "treatment_type": {
                            "type": "string",
                            "description": "Treatment or department name, e.g. Ayurvedic Oncology, Spine Care, or Ksharasoothra"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Symptoms, complaint, or preferred branch (Alappuzha or Trivandrum)"
                        }
                    }
                }
            }
        }
    }

    try:
        res2 = post_json("https://api.elevenlabs.io/v1/convai/tools", tool_book_payload)
        tool2_id = res2.get("id")
        print(f"✅ Created book_appointment tool: {tool2_id}")
    except Exception as e:
        print(f"❌ Error creating book_appointment tool: {e}")
        tool2_id = None

    # 3. Create Agent
    tools = []
    if tool1_id:
        tools.append({"tool_id": tool1_id, "type": "webhook"})
    if tool2_id:
        tools.append({"tool_id": tool2_id, "type": "webhook"})

    agent_payload = {
        "name": "Asha - Sreerudra Ayurveda AI Receptionist",
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": SREERUDRA_PROMPT,
                    "tools": tools
                },
                "first_message": FIRST_MESSAGE,
                "language": "en"
            },
            "tts": {
                "voice_id": "eXpIbVcVbLo8ZJQDlDnl",
                "model_id": "eleven_v3_conversational"
            },
            "asr": {
                "quality": "high",
                "provider": "scribe_realtime",
                "user_input_audio_format": "pcm_16000"
            }
        }
    }

    try:
        agent_res = post_json("https://api.elevenlabs.io/v1/convai/agents/create", agent_payload)
        agent_id = agent_res.get("agent_id")
        print(f"🎉 SUCCESS! Agent Created! Agent ID: {agent_id}")
        return agent_id, tool1_id, tool2_id
    except urllib.error.HTTPError as e:
        print(f"❌ HTTPError creating agent: {e.code} {e.read().decode()}")
        return None, tool1_id, tool2_id
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return None, tool1_id, tool2_id


if __name__ == "__main__":
    setup()

