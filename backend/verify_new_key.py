import urllib.request
import json

API_KEY = "sk_0ede1042eedf868a46eeb296409ef6d7e63366596f554649"

req = urllib.request.Request(
    "https://api.elevenlabs.io/v1/user/subscription",
    headers={"xi-api-key": API_KEY}
)

try:
    with urllib.request.urlopen(req) as resp:
        sub = json.loads(resp.read())
        print("=== NEW ELEVENLABS ACCOUNT SUBSCRIPTION ===")
        print("Tier:", sub.get("tier"))
        print("Character count:", sub.get("character_count"), "/", sub.get("character_limit"))
        print("Status:", sub.get("status"))
except Exception as e:
    print("Error verifying new key:", e)

