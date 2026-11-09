"""Create agent with tool_ids on new account using Alice voice."""

import json
import urllib.request
import urllib.error

NEW_API_KEY = "sk_0ede1042eedf868a46eeb296409ef6d7e63366596f554649"
TOOL_CHECK = "tool_0201m70069cmfjnr38jshd5vkf21"
TOOL_BOOK = "tool_2701m70069x9e1wvrwhrc9napt7m"

from backend.migrate_to_new_account import SREERUDRA_PROMPT, FIRST_MESSAGE

payload = {
    "name": "Asha - Sreerudra Ayurveda AI Receptionist",
    "conversation_config": {
        "agent": {
            "prompt": {
                "prompt": SREERUDRA_PROMPT,
                "tool_ids": [TOOL_CHECK, TOOL_BOOK]
            },
            "first_message": FIRST_MESSAGE,
            "language": "en"
        },
        "tts": {
            "voice_id": "Xb7hH8MSUJpSbSDYk0k2",
            "model_id": "eleven_v3_conversational"
        },
        "asr": {
            "quality": "high",
            "provider": "scribe_realtime",
            "user_input_audio_format": "pcm_16000"
        }
    }
}

req = urllib.request.Request(
    "https://api.elevenlabs.io/v1/convai/agents/create",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "xi-api-key": NEW_API_KEY,
        "Content-Type": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read())
        agent_id = res.get("agent_id")
        print("🎉 SUCCESS! Created agent ID:", agent_id)
        with open("new_agent_id.txt", "w") as f:
            f.write(agent_id)
except urllib.error.HTTPError as e:
    print("HTTP Error", e.code, e.read().decode())
except Exception as e:
    print("Error:", e)
