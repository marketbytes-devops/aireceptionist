import pytest
from sqlalchemy import select
from backend.app.models.clinic import Clinic
from backend.app.models.call_log import CallLog


@pytest.mark.asyncio
async def test_incoming_twilio_call(client, test_db):
    clinic_res = await test_db.execute(select(Clinic).limit(1))
    clinic = clinic_res.scalar_one()

    # Form-encoded webhook data from Twilio
    form_data = {
        "CallSid": "CA1234567890abcdef",
        "From": "+919876543210",
        "To": clinic.phone_number,
    }

    response = await client.post(
        "/api/v1/telephony/incoming-call",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    assert "<Connect>" in response.text
    assert "<Stream" in response.text
    assert f"/api/v1/telephony/media-stream/{clinic.id}" in response.text


@pytest.mark.asyncio
async def test_elevenlabs_post_call_webhook(client, test_db):
    clinic_res = await test_db.execute(select(Clinic).limit(1))
    clinic = clinic_res.scalar_one()

    # Simulated ElevenLabs post-call payload
    payload = {
        "call_id": "conv_987654321",
        "call_sid": "CA1234567890abcdef",
        "clinic_id": str(clinic.id),
        "caller_phone": "+919876543210",
        "duration_secs": 128,
        "recording_url": "https://api.elevenlabs.io/recordings/conv_987654321.mp3",
        "transcript": [
            {"role": "agent", "message": "Namaste! Welcome to AyurVoice Test Clinic. How may I assist you today?"},
            {"role": "user", "message": "Hello, I want to book an appointment with Dr. Varma on Monday."},
            {"role": "agent", "message": "Dr. Varma is available at 10:00 AM on Monday. Shall I book that for you?"},
            {"role": "user", "message": "Yes, please confirm it under Kavita Raman."}
        ],
        "analysis": {
            "transcript_summary": "Patient Kavita Raman called to schedule an Ayurvedic consultation with Dr. Varma.",
            "sentiment": "positive"
        }
    }

    response = await client.post("/api/v1/webhooks/elevenlabs-post-call", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

    # Verify CallLog is updated
    call_log_res = await test_db.execute(
        select(CallLog).where(CallLog.call_sid == "CA1234567890abcdef")
    )
    call_log = call_log_res.scalar_one_or_none()
    assert call_log is not None
    assert call_log.duration_seconds == 128
    assert "Patient Kavita Raman called" in call_log.summary
    assert call_log.sentiment == "positive"

