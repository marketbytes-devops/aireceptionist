import os
import sys

# Ensure workspace root is always in sys.path
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import asyncio
from decimal import Decimal
from datetime import time
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.app.main import app
from backend.app.core.database import get_db
from backend.app.models.base import Base
from backend.app.models.clinic import Clinic
from backend.app.models.doctor import Doctor
from backend.app.models.schedule import DoctorSchedule
from backend.app.models.user import User, UserRole
from backend.app.core.security import get_password_hash

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        # Seed test clinic
        clinic = Clinic(
            name="AyurVoice Test Clinic",
            slug="ayurvoice-test-clinic",
            phone_number="+15551234567",
            address="Test Ayurvedic Center",
            timezone="Asia/Kolkata"
        )
        session.add(clinic)
        await session.flush()

        # Seed test admin user
        user = User(
            email="testadmin@ayurvoice.com",
            hashed_password=get_password_hash("TestPass123!"),
            full_name="Dr. Test Admin",
            role=UserRole.CLINIC_ADMIN,
            clinic_id=clinic.id,
            is_active=True
        )
        session.add(user)

        # Seed test doctor
        doctor = Doctor(
            clinic_id=clinic.id,
            name="Dr. Varma",
            specialization="Panchakarma Specialist",
            consultation_fee=Decimal("500.00"),
            is_active=True
        )
        session.add(doctor)
        await session.flush()

        # Seed test doctor schedule: Monday (0) to Friday (4), 10:00 to 14:00, 30 min slots
        for day in range(5):
            sched = DoctorSchedule(
                doctor_id=doctor.id,
                day_of_week=day,
                start_time=time(10, 0),
                end_time=time(14, 0),
                slot_duration_minutes=30,
                is_active=True
            )
            session.add(sched)

        await session.commit()
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

