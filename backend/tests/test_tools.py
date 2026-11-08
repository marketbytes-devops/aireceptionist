import pytest
from datetime import datetime, timedelta
from sqlalchemy import select
from backend.app.models.clinic import Clinic
from backend.app.models.doctor import Doctor
from backend.app.models.appointment import Appointment


@pytest.mark.asyncio
async def test_check_availability_tool(client, test_db):
    # Fetch seeded clinic
    clinic_res = await test_db.execute(select(Clinic).limit(1))
    clinic = clinic_res.scalar_one()

    # Find the next Monday date
    today = datetime.now()
    days_ahead = (0 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    next_monday = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    # 1. Check availability with doctor name and date
    payload = {
        "clinic_id": str(clinic.id),
        "doctor_name": "Dr. Varma",
        "date_time": f"{next_monday}T10:00:00",
        "treatment_type": "Panchakarma Consultation"
    }
    response = await client.post("/api/v1/tools/check-availability", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is True
    assert "Dr. Varma is available" in data["message"]
    assert len(data["available_slots"]) > 0


@pytest.mark.asyncio
async def test_book_appointment_tool(client, test_db):
    clinic_res = await test_db.execute(select(Clinic).limit(1))
    clinic = clinic_res.scalar_one()

    today = datetime.now()
    days_ahead = (0 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    next_monday = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    # 1. Book an appointment
    book_payload = {
        "clinic_id": str(clinic.id),
        "doctor_name": "Dr. Varma",
        "patient_name": "Kavita Raman",
        "patient_phone": "+919876543210",
        "patient_email": "kavita@example.com",
        "appointment_time": f"{next_monday}T10:30:00",
        "treatment_type": "Nadi Pariksha & Pulse Diagnosis",
        "notes": "Complaining of chronic backache."
    }

    response = await client.post("/api/v1/tools/book-appointment", json=book_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["confirmation_id"].startswith("AYUR-")
    assert "Dr. Varma" in data["doctor_name"]

    # 2. Verify appointment persisted in database
    app_res = await test_db.execute(
        select(Appointment).where(Appointment.patient_name == "Kavita Raman")
    )
    saved_appointment = app_res.scalar_one_or_none()
    assert saved_appointment is not None
    assert saved_appointment.status.value == "booked"

    # 3. Test double booking prevention (attempt to book the same slot again)
    conflict_response = await client.post("/api/v1/tools/book-appointment", json=book_payload)
    assert conflict_response.status_code == 409

