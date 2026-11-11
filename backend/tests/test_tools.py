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


@pytest.mark.asyncio
async def test_full_reschedule_cancel_escalate_flow(client, test_db):
    today = datetime.now()
    days_ahead = (0 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    next_monday = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    # 1. Book WITHOUT clinic_id (tests null-safe clinic fallback + patient_age)
    book_payload = {
        "patient_name": "Anil Menon",
        "patient_age": "45",
        "patient_phone": "+91 98470 11223",
        "appointment_time": f"{next_monday}T11:00:00",
        "treatment_type": "Spine Care",
        "notes": "Lower backache"
    }
    book_res = await client.post("/api/v1/tools/book-appointment", json=book_payload)
    assert book_res.status_code == 201
    book_data = book_res.json()
    app_id = book_data["appointment_id"]

    # 2. Find appointment using only 10-digit normalized phone
    find_res = await client.post("/api/v1/tools/find-appointment", json={
        "patient_phone": "9847011223"
    })
    assert find_res.status_code == 200
    find_data = find_res.json()
    assert find_data["found"] is True
    assert len(find_data["appointments"]) >= 1
    assert find_data["appointments"][0]["patient_name"] == "Anil Menon"

    # 3. Reschedule to 14:30:00
    resched_res = await client.post("/api/v1/tools/reschedule-appointment", json={
        "appointment_id": app_id,
        "new_appointment_time": f"{next_monday}T14:30:00"
    })
    assert resched_res.status_code == 200
    resched_data = resched_res.json()
    assert resched_data["status"] == "success"
    assert "14:30" in resched_data["new_appointment_time"]

    # 4. Cancel the appointment
    cancel_res = await client.post("/api/v1/tools/cancel-appointment", json={
        "patient_phone": "9847011223",
        "reason": "Patient requested cancellation"
    })
    assert cancel_res.status_code == 200
    cancel_data = cancel_res.json()
    assert cancel_data["status"] == "success"

    # Verify cancelled in DB
    app_res = await test_db.execute(select(Appointment).where(Appointment.id == app_id))
    saved = app_res.scalar_one()
    assert saved.status.value == "cancelled"

    # 5. Escalate to Staff
    esc_res = await client.post("/api/v1/tools/escalate-to-staff", json={
        "patient_name": "Suresh Nair",
        "patient_phone": "+919000011111",
        "reason": "Severe post-stroke breathing trouble",
        "urgency": "emergency",
        "branch": "Alappuzha"
    })
    assert esc_res.status_code == 200
    esc_data = esc_res.json()
    assert esc_data["status"] == "escalated"
    assert esc_data["ticket_id"].startswith("ESC-")
    assert "+91 98479 48218" in esc_data["helpline_number"]


