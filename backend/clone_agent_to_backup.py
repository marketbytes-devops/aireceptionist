"""Clone Asha Agent and all webhook tools from Primary ElevenLabs account to Backup ElevenLabs account."""

import json
import httpx

PRIMARY_API_KEY = "sk_93285b98db548cb882a2c1f1628e0b4b47e391be71028391"
PRIMARY_AGENT_ID = "agent_0901m79nh3fcfhj9yn7f6ktqggfx"

BACKUP_API_KEY = "sk_f08760084a19b8c3d45363d9012795942f1f7848f9b53c87"


def clone():
    print("1. Fetching tools from Primary Account...")
    res = httpx.get(
        "https://api.elevenlabs.io/v1/convai/tools",
        headers={"xi-api-key": PRIMARY_API_KEY},
        timeout=30.0
    )
    res.raise_for_status()
    primary_tools = res.json().get("tools", [])
    print(f"   Found {len(primary_tools)} tools.")

    # Check existing tools on Backup account
    existing_res = httpx.get(
        "https://api.elevenlabs.io/v1/convai/tools",
        headers={"xi-api-key": BACKUP_API_KEY},
        timeout=30.0
    )
    existing_tools = {t.get("tool_config", {}).get("name"): t.get("id") for t in existing_res.json().get("tools", [])}

    backup_tool_ids = []
    for tool in primary_tools:
        name = tool.get("tool_config", {}).get("name")
        if name in existing_tools:
            tool_id = existing_tools[name]
            print(f"2. Tool '{name}' already exists on Backup Account -> {tool_id}")
            backup_tool_ids.append(tool_id)
            continue

        print(f"2. Creating tool '{name}' on Backup Account...")
        create_payload = {
            "tool_config": tool.get("tool_config")
        }
        create_res = httpx.post(
            "https://api.elevenlabs.io/v1/convai/tools",
            headers={"xi-api-key": BACKUP_API_KEY},
            json=create_payload,
            timeout=30.0
        )
        if create_res.status_code not in (200, 201):
            print(f"   Error: {create_res.status_code} {create_res.text}")
            create_res.raise_for_status()
        new_id = create_res.json().get("id")
        print(f"   ✅ Created tool '{name}' -> {new_id}")
        backup_tool_ids.append(new_id)

    # Fetch Agent from Primary Account
    print("3. Fetching Agent configuration from Primary Account...")
    agent_res = httpx.get(
        f"https://api.elevenlabs.io/v1/convai/agents/{PRIMARY_AGENT_ID}",
        headers={"xi-api-key": PRIMARY_API_KEY},
        timeout=30.0
    )
    agent_res.raise_for_status()
    agent_data = agent_res.json()

    conv_config = agent_data.get("conversation_config", {})
    # Update tool_ids in conv_config
    if "agent" in conv_config:
        agent_block = conv_config["agent"]
        if "tools" in agent_block:
            del agent_block["tools"]
        if "prompt" in agent_block and isinstance(agent_block["prompt"], dict):
            if "tools" in agent_block["prompt"]:
                del agent_block["prompt"]["tools"]
            agent_block["prompt"]["tool_ids"] = backup_tool_ids

    print("4. Creating Asha Agent on Backup Account...")
    new_agent_payload = {
        "name": agent_data.get("name", "Asha - Sreerudra Ayurveda AI Receptionist (Backup)"),
        "conversation_config": conv_config
    }

    create_agent_res = httpx.post(
        "https://api.elevenlabs.io/v1/convai/agents/create",
        headers={"xi-api-key": BACKUP_API_KEY},
        json=new_agent_payload,
        timeout=30.0
    )
    if create_agent_res.status_code not in (200, 201):
        print(f"   Error creating agent: {create_agent_res.status_code} {create_agent_res.text}")
        create_agent_res.raise_for_status()

    backup_agent_id = create_agent_res.json().get("agent_id")
    print("\n🎉 SUCCESS! Backup Agent created successfully!")
    print(f"   BACKUP_AGENT_ID: {backup_agent_id}")
    return backup_agent_id


if __name__ == "__main__":
    clone()
