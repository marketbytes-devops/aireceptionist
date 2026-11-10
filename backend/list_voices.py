import urllib.request
import json

req = urllib.request.Request(
    "https://api.elevenlabs.io/v1/voices",
    headers={"xi-api-key": "sk_0ede1042eedf868a46eeb296409ef6d7e63366596f554649"}
)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())
    voices = data.get("voices", [])
    print(f"Total voices: {len(voices)}")
    for v in voices:
        print(f"{v.get('voice_id')}: {v.get('name')} | {v.get('labels', {}).get('gender')} | {v.get('labels', {}).get('accent')}")

