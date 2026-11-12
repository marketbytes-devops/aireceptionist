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


@pytest.mark.asyncio
async def test_knowledge_base_sync_locks_v4_turbo_malayalam_voice(client, test_db, monkeypatch):
    from backend.app.api.v1 import clinics as clinics_api
    from backend.app.core.elevenlabs_config import DEFAULT_MALAYALAM_VOICE_ID, DEFAULT_TTS_MODEL_ID

    clinic_res = await test_db.execute(select(Clinic).limit(1))
    clinic = clinic_res.scalar_one()

    captured = {}

    class DummyResponse:
        status_code = 200

    class DummyAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def patch(self, url, headers=None, json=None):
            captured["url"] = url
            captured["json"] = json
            return DummyResponse()

    monkeypatch.setattr(clinics_api.settings, "ELEVENLABS_API_KEY", "sk_test_key")
    monkeypatch.setattr(clinics_api.settings, "ELEVENLABS_AGENT_ID", "agent_test_id")
    monkeypatch.setattr(clinics_api.httpx, "AsyncClient", DummyAsyncClient)

    response = await client.put(
        f"/api/v1/clinics/{clinic.id}/knowledge-base",
        json={"knowledge_base": "Hospital hours: 9 AM - 5 PM", "sync_to_elevenlabs": True},
    )
    assert response.status_code == 200
    assert response.json()["sync_status"] == "synced_to_elevenlabs"

    cfg = captured["json"]["conversation_config"]
    prompt_text = cfg["agent"]["prompt"]["prompt"]
    assert cfg["agent"]["language"] == "ml"
    assert "{{time_greeting_ml}}" in cfg["agent"]["first_message"]
    assert "time_greeting_ml" in cfg["agent"]["dynamic_variables"]["dynamic_variable_placeholders"]
    assert "EMOTIONAL ADAPTATION" in prompt_text
    assert "ADDRESS PROBLEM OR QUESTION FIRST" in prompt_text
    assert "ASK PREFERRED BRANCH NEXT" in prompt_text
    assert prompt_text.index("ASK PREFERRED BRANCH NEXT") < prompt_text.index("COLLECT PATIENT DETAILS AFTER PROBLEM & BRANCH")
    assert cfg["tts"]["model_id"] == DEFAULT_TTS_MODEL_ID
    assert cfg["tts"]["voice_id"] == DEFAULT_MALAYALAM_VOICE_ID
    assert cfg["tts"]["expressive_mode"] is False
    assert cfg["tts"]["stability"] == 0.85
    assert cfg["tts"]["similarity_boost"] == 0.9
    assert cfg["tts"]["clone_strength"] == 0.5


def test_ist_time_of_day_greetings():
    from datetime import datetime
    from backend.app.core.elevenlabs_config import (
        IST_TIMEZONE,
        build_conversation_initiation_payload,
        get_ist_time_greeting,
    )

    morning = get_ist_time_greeting(datetime(2026, 11, 12, 8, 30, tzinfo=IST_TIMEZONE))
    assert morning["time_period"] == "morning"
    assert morning["time_greeting_en"] == "Good morning"
    assert "ഗുഡ് മോർണിംഗ്" in morning["time_greeting_ml"]

    afternoon = get_ist_time_greeting(datetime(2026, 11, 12, 15, 8, tzinfo=IST_TIMEZONE))
    assert afternoon["time_period"] == "afternoon"
    assert afternoon["time_greeting_en"] == "Good afternoon"
    assert "ഗുഡ് ആഫ്റ്റർനൂൺ" in afternoon["time_greeting_ml"]

    evening = get_ist_time_greeting(datetime(2026, 11, 12, 19, 45, tzinfo=IST_TIMEZONE))
    assert evening["time_period"] == "evening"
    assert evening["time_greeting_en"] == "Good evening"
    assert "ഗുഡ് ഈവനിംഗ്" in evening["time_greeting_ml"]

    late_night = get_ist_time_greeting(datetime(2026, 11, 12, 4, 59, tzinfo=IST_TIMEZONE))
    assert late_night["time_period"] == "evening"

    ws_payload = build_conversation_initiation_payload(
        datetime(2026, 11, 12, 15, 8, tzinfo=IST_TIMEZONE)
    )
    assert ws_payload["type"] == "conversation_initiation_client_data"
    assert ws_payload["dynamic_variables"]["time_period"] == "afternoon"



