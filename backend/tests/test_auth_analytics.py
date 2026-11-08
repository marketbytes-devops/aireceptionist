import pytest
from sqlalchemy import select
from backend.app.models.clinic import Clinic
from backend.app.models.user import User


@pytest.mark.asyncio
async def test_auth_login_and_me(client, test_db):
    # 1. Login with seeded test admin credentials
    login_payload = {
        "email": "testadmin@ayurvoice.com",
        "password": "TestPass123!"
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["email"] == "testadmin@ayurvoice.com"

    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Query /me endpoint
    me_response = await client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "testadmin@ayurvoice.com"

    # 3. Query /analytics/dashboard
    dash_response = await client.get("/api/v1/analytics/dashboard", headers=headers)
    assert dash_response.status_code == 200
    dash_data = dash_response.json()
    assert "total_calls_today" in dash_data
    assert "active_doctors" in dash_data
    assert "appointments_booked_today" in dash_data

