import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.core.security import get_password_hash
from backend.app.models.clinic import Clinic
from backend.app.models.doctor import Doctor
from backend.app.models.schedule import DoctorSchedule
from backend.app.models.user import User, UserRole
from backend.app.schemas.clinic import ClinicCreate, ClinicUpdate, ClinicResponse, ClinicKnowledgeBaseUpdate
from backend.app.core.config import settings
from backend.app.core.elevenlabs_config import build_elevenlabs_agent_patch
import httpx
from backend.app.schemas.doctor import DoctorResponse
from backend.app.schemas.schedule import DoctorScheduleResponse
from backend.app.api.deps import get_current_user, get_current_clinic_admin

router = APIRouter(prefix="/clinics", tags=["Clinics"])


@router.post("", response_model=ClinicResponse, status_code=status.HTTP_201_CREATED)
async def register_clinic(
    clinic_in: ClinicCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Register a new Ayurvedic clinic (with optional initial clinic admin user)."""
    # Check if slug or phone number already in use
    slug_stmt = select(Clinic).where(Clinic.slug == clinic_in.slug)
    slug_res = await db.execute(slug_stmt)
    if slug_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A clinic with this slug already exists."
        )

    phone_stmt = select(Clinic).where(Clinic.phone_number == clinic_in.phone_number)
    phone_res = await db.execute(phone_stmt)
    if phone_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A clinic with this phone number is already registered."
        )

    clinic = Clinic(
        name=clinic_in.name,
        slug=clinic_in.slug,
        phone_number=clinic_in.phone_number,
        address=clinic_in.address,
        timezone=clinic_in.timezone
    )
    db.add(clinic)
    await db.flush()

    # Optionally create initial clinic admin user
    if clinic_in.admin_email and clinic_in.admin_password:
        admin_user = User(
            email=clinic_in.admin_email,
            hashed_password=get_password_hash(clinic_in.admin_password),
            full_name=clinic_in.admin_name or f"{clinic.name} Admin",
            role=UserRole.CLINIC_ADMIN,
            clinic_id=clinic.id,
            is_active=True
        )
        db.add(admin_user)

    await db.commit()
    await db.refresh(clinic)
    return clinic


@router.get("", response_model=List[ClinicResponse])
async def list_clinics(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List registered clinics."""
    stmt = select(Clinic).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/{clinic_id}", response_model=ClinicResponse)
async def get_clinic_by_id(
    clinic_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get clinic details by ID."""
    stmt = select(Clinic).where(Clinic.id == clinic_id)
    res = await db.execute(stmt)
    clinic = res.scalar_one_or_none()
    if not clinic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found.")
    return clinic


@router.get("/{clinic_id}/schedule", response_model=List[DoctorResponse])
async def get_clinic_doctors_schedule(
    clinic_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Fetch complete doctors schedule and availability for a clinic."""
    clinic_stmt = select(Clinic).where(Clinic.id == clinic_id)
    c_res = await db.execute(clinic_stmt)
    if not c_res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found.")

    doc_stmt = (
        select(Doctor)
        .where(Doctor.clinic_id == clinic_id)
        .options(selectinload(Doctor.schedules))
    )
    doc_res = await db.execute(doc_stmt)
    doctors = doc_res.scalars().all()
    return doctors


@router.get("/{clinic_id}/knowledge-base")
async def get_clinic_knowledge_base(
    clinic_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve the current knowledge base and clinic details for AI receptionist."""
    stmt = select(Clinic).where(Clinic.id == clinic_id)
    res = await db.execute(stmt)
    clinic = res.scalar_one_or_none()
    if not clinic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found.")

    return {
        "clinic_id": str(clinic.id),
        "name": clinic.name,
        "phone_number": clinic.phone_number,
        "address": clinic.address,
        "knowledge_base": clinic.knowledge_base or ""
    }


@router.put("/{clinic_id}/knowledge-base")
async def update_clinic_knowledge_base(
    clinic_id: uuid.UUID,
    payload: ClinicKnowledgeBaseUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update clinic knowledge base and optionally sync directly to ElevenLabs Agent in real time."""
    stmt = select(Clinic).where(Clinic.id == clinic_id)
    res = await db.execute(stmt)
    clinic = res.scalar_one_or_none()
    if not clinic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found.")

    clinic.knowledge_base = payload.knowledge_base
    await db.commit()
    await db.refresh(clinic)

    sync_status = "saved_locally"
    sync_message = "Knowledge base saved in database."

    # If sync to ElevenLabs requested and credentials exist
    if payload.sync_to_elevenlabs and settings.ELEVENLABS_API_KEY and settings.ELEVENLABS_AGENT_ID:
        try:
            # Build unified bilingual system prompt with updated clinic knowledge base
            unified_prompt = (
                "# Language Rules\n"
                "- You are Asha, the warm, polite, and professional AI voice receptionist for "
                f"{clinic.name}.\n"
                "- You are fully fluent in both Malayalam (മലയാളം) and English.\n"
                "- If the caller speaks Malayalam (or Manglish), or asks if you speak Malayalam, ALWAYS reply in natural, polite Malayalam.\n"
                "- If the caller speaks English, reply in polite English.\n"
                "- Keep spoken responses concise (1 to 2 sentences per turn).\n\n"
                "# Clinic Knowledge Base & Facts\n"
                f"{clinic.knowledge_base}\n\n"
                "# Background Noise & Acoustic Recovery Rules\n"
                "- Focus exclusively on the primary caller's voice and completely ignore ambient background sounds, TV chatter, room echoes, traffic, and fan noise.\n"
                "- If the caller speaks over you or interrupts you with clear intent, immediately pause and listen to their question.\n"
                "- If background noise drowns out the caller, or if their response is muffled, cut off, or inaudible, NEVER guess, hallucinate, or assume what they said.\n"
                "- Politely ask the caller to repeat in natural, respectful Malayalam:\n"
                "  \"ക്ഷമിക്കണം, ബാക്ക്ഗ്രൗണ്ട് സൗണ്ട് കാരണം വ്യക്തമായി കേൾക്കാൻ സാധിച്ചില്ല. ഒന്നുകൂടി പറയാമോ?\"\n"
                "- If the caller spoke in English, ask in English:\n"
                "  \"I am sorry, I could not hear you clearly due to background noise. Could you please repeat that?\"\n\n"
                "# Receptionist Call Flow & Tools Instructions (5-Branch Workflow)\n"
                "- Keep introductions short and natural. Adapt to each caller's tone and urgency.\n"
                "- If a caller interrupts or immediately asks a specific question (such as doctor timings, fees, booking, reschedule, cancel, or emergency), answer or jump directly to that branch right away without repeating menus.\n"
                "- If a caller only says hello without specifying what they need, briefly ask if they want to Book, Reschedule, Cancel, or get Hospital Info / Staff Help.\n"
                f"- When checking doctor slots, pass clinic_id '{str(clinic.id)}' to 'check_availability'.\n"
                "- BOOKING: First collect Patient Name, Age (patient_age), and Phone Number, then Doctor/Specialty & Branch. Check availability with 'check_availability', confirm a slot, and call 'book_appointment'. Share the confirmation ID and wish them good health.\n"
                "- RESCHEDULING: First verify patient Phone/Name and call 'find_appointment'. Read existing details, check new slots with 'check_availability', confirm with caller, and call 'reschedule_appointment'.\n"
                "- CANCELLING: Verify patient Phone/Name via 'find_appointment', read existing details, ask explicit confirmation ('നിലവിലുള്ള ഈ അപ്പോയിന്റ്മെന്റ് റദ്ദാക്കാൻ താങ്കൾക്ക് സമ്മതമാണോ?' / 'Are you sure you want to cancel?'), and only after YES call 'cancel_appointment'.\n"
                "- STAFF ESCALATION / EMERGENCIES: For medical emergencies, human staff requests, or special doubts, collect Name/Phone/Reason and call 'escalate_to_staff', then share helpline +91 90379 03333."
            )

            elevenlabs_url = f"https://api.elevenlabs.io/v1/convai/agents/{settings.ELEVENLABS_AGENT_ID}"
            patch_data = build_elevenlabs_agent_patch(
                prompt=unified_prompt,
                voice_id=settings.ELEVENLABS_VOICE_ID or None,
                model_id=settings.ELEVENLABS_TTS_MODEL_ID or None,
            )

            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.patch(
                    elevenlabs_url,
                    headers={
                        "xi-api-key": settings.ELEVENLABS_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json=patch_data
                )
                if resp.status_code in (200, 201):
                    sync_status = "synced_to_elevenlabs"
                    sync_message = "Knowledge base saved and synced to AI Receptionist in real time!"
                else:
                    sync_status = "sync_failed"
                    sync_message = f"Saved in database, but ElevenLabs sync returned status {resp.status_code}."
        except Exception as e:
            sync_status = "sync_error"
            sync_message = f"Saved in database, but sync encountered error: {str(e)}"

    return {
        "status": "success",
        "sync_status": sync_status,
        "message": sync_message,
        "clinic_id": str(clinic.id),
        "knowledge_base": clinic.knowledge_base
    }

