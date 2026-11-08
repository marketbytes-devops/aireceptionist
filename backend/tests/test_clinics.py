import pytest
from sqlalchemy import select
from backend.app.models.clinic import Clinic


@pytest.mark.asyncio
async def test_register_clinic(client, test_db):
    new_clinic_payload = {
        "name": "Kottakkal Arya Vaidya Sala Branch",
        "slug": "kottakkal-branch-1",
        "phone_number": "+18889990011",
        "address": "Kottakkal, Malappuram, Kerala",
        "timezone": "Asia/Kolkata",
        "admin_name": "Chief Vaidya",
        "admin_email": "vaidya@kottakkal.example",
        "admin_password": "SecurePassword123!"
    }

    response = await client.post("/api/v1/clinics", json=new_clinic_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == new_clinic_payload["name"]
    assert data["slug"] == new_clinic_payload["slug"]


@pytest.mark.asyncio
async def test_get_clinic_schedule(client, test_db):
    clinic_res = await test_db.execute(select(Clinic).limit(1))
    clinic = clinic_res.scalar_one()

    response = await client.get(f"/api/v1/clinics/{clinic.id}/schedule")
    assert response.status_code == 200
    doctors_list = response.json()
    assert len(doctors_list) >= 1
    assert "schedules" in doctors_list[0]

