import os
import sys

# Ensure parent directory (project root) is on sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_current_dir)
_root_dir = os.path.dirname(_backend_dir)
for _p in [_root_dir, _backend_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from contextlib import asynccontextmanager
from decimal import Decimal
from datetime import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from backend.app.core.config import settings
from backend.app.core.database import init_db, AsyncSessionLocal
from backend.app.core.security import get_password_hash
from backend.app.models.clinic import Clinic
from backend.app.models.doctor import Doctor
from backend.app.models.schedule import DoctorSchedule
from backend.app.models.user import User, UserRole
from backend.app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist
    await init_db()

    # Seed initial demo Ayurvedic clinic and specialist doctor if empty
    async with AsyncSessionLocal() as session:
        clinic_stmt = select(Clinic).limit(1)
        res = await session.execute(clinic_stmt)
        existing_clinic = res.scalar_one_or_none()

        if not existing_clinic:
            # 1. Create Default Clinic
            demo_clinic = Clinic(
                name="Sree Kerala Ayurvedic Clinic",
                slug="sree-kerala-ayurveda",
                phone_number="+18005550199",
                address="108 Dhanwantari Road, Fort Kochi, Kerala, 682001",
                timezone="Asia/Kolkata"
            )
            session.add(demo_clinic)
            await session.flush()

            # 2. Create Default Clinic Admin User
            admin_user = User(
                email="admin@ayurvoice.com",
                hashed_password=get_password_hash("AyurVoice2026!"),
                full_name="Dr. Rajesh Varma (Clinic Admin)",
                role=UserRole.CLINIC_ADMIN,
                clinic_id=demo_clinic.id,
                is_active=True
            )
            session.add(admin_user)

            # 3. Create Specialist Ayurvedic Doctors
            doc1 = Doctor(
                clinic_id=demo_clinic.id,
                name="Dr. Rajesh Varma",
                specialization="Panchakarma & Pulse Diagnosis Specialist",
                consultation_fee=Decimal("600.00"),
                bio="BAMS, MD (Ayurveda) with 18+ years experience in authentic Kerala Panchakarma therapies.",
                is_active=True
            )
            doc2 = Doctor(
                clinic_id=demo_clinic.id,
                name="Dr. Ananya Nair",
                specialization="Ayurvedic Dietetics & Skin Wellness",
                consultation_fee=Decimal("500.00"),
                bio="Expert in herbal pharmacology and holistic lifestyle coaching.",
                is_active=True
            )
            session.add_all([doc1, doc2])
            await session.flush()

            # 4. Create Schedules: Monday - Saturday (0 to 5), 09:00 to 17:00, 30 min slots
            for day in range(6):  # Monday through Saturday
                s1 = DoctorSchedule(
                    doctor_id=doc1.id,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    slot_duration_minutes=30,
                    is_active=True
                )
                s2 = DoctorSchedule(
                    doctor_id=doc2.id,
                    day_of_week=day,
                    start_time=time(10, 0),
                    end_time=time(18, 0),
                    slot_duration_minutes=30,
                    is_active=True
                )
                session.add_all([s1, s2])

            await session.commit()
            print("Successfully initialized database with demo clinic, doctors, and schedules!")

    yield
    # Shutdown logic if needed


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Multi-Tenant AI Voice Receptionist Platform for Ayurvedic Clinics powered by ElevenLabs & Twilio.",
    lifespan=lifespan
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://aireceptionist.marketbytes.in",
        "http://aireceptionist.marketbytes.in",
    ],
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
async def root():
    return {
        "platform": settings.PROJECT_NAME,
        "status": "online",
        "docs_url": "/docs",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

