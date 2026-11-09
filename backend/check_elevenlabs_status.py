import urllib.request
import json

API_KEY = 'sk_264db99659f0453786d1c1d04e1fad3f8d4e5bfce5da3137'
AGENT_ID = 'agent_3601m6rj4cg6f9brv5kx93ykgag7'

# 1. Check User Subscription & Quota
try:
    req = urllib.request.Request('https://api.elevenlabs.io/v1/user/subscription', headers={'xi-api-key': API_KEY})
    with urllib.request.urlopen(req) as resp:
        sub = json.loads(resp.read())
        print('=== ELEVENLABS SUBSCRIPTION ===')
        print('Tier:', sub.get('tier'))
        print('Character count:', sub.get('character_count'), '/', sub.get('character_limit'))
        print('Status:', sub.get('status'))
        print('Next invoice reset:', sub.get('next_invoice'))
except Exception as e:
    print('Subscription check error:', e)

# 2. Check Agent Details
try:
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}', headers={'xi-api-key': API_KEY})
    with urllib.request.urlopen(req) as resp:
        ag = json.loads(resp.read())
        print('\n=== AGENT DETAILS ===')
        print('Agent Name:', ag.get('name'))
        print('Agent ID:', ag.get('agent_id'))
        print('Conversation Config keys:', list(ag.get('conversation_config', {}).keys()))
except Exception as e:
    print('Agent check error:', e)

# 3. Check Phone Numbers
try:
    req = urllib.request.Request('https://api.elevenlabs.io/v1/convai/phone-numbers', headers={'xi-api-key': API_KEY})
    with urllib.request.urlopen(req) as resp:
        pns = json.loads(resp.read())
        print('\n=== PHONE NUMBERS IN ELEVENLABS ===')
        print(json.dumps(pns, indent=2))
except Exception as e:
    print('Phone numbers error:', e)

