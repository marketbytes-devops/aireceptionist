"""Shared ElevenLabs Conversational AI configuration defaults and payload builders."""

from typing import Any, Optional

DEFAULT_MALAYALAM_VOICE_ID = "896Jb7AxcYyesi7deFZe"  # Amara - Female Malayalam (Eleven v4 PVC)
DEFAULT_TTS_MODEL_ID = "eleven_v4_turbo"
DEFAULT_AGENT_LANGUAGE = "ml"

DEFAULT_TTS_CONFIG: dict[str, Any] = {
    "model_id": DEFAULT_TTS_MODEL_ID,
    "voice_id": DEFAULT_MALAYALAM_VOICE_ID,
    "expressive_mode": False,
    "stability": 0.85,
    "similarity_boost": 0.9,
    "clone_strength": 0.5,
}

DEFAULT_TURN_CONFIG: dict[str, Any] = {
    "turn_eagerness": "patient",
    "speculative_turn": False,
    "turn_timeout": 7.0,
}


def build_elevenlabs_agent_patch(
    *,
    prompt: str,
    voice_id: Optional[str] = None,
    model_id: Optional[str] = None,
    language: str = DEFAULT_AGENT_LANGUAGE,
    tool_ids: Optional[list[str]] = None,
    first_message: Optional[str] = None,
    disable_first_message_interruptions: Optional[bool] = None,
    agent_name: Optional[str] = None,
) -> dict[str, Any]:
    """Build a canonical PATCH payload that locks TTS to a single v4 voice/model."""
    prompt_cfg: dict[str, Any] = {"prompt": prompt}
    if tool_ids is not None:
        prompt_cfg["tool_ids"] = tool_ids

    agent_cfg: dict[str, Any] = {
        "prompt": prompt_cfg,
        "language": language,
    }
    if first_message is not None:
        agent_cfg["first_message"] = first_message
    if disable_first_message_interruptions is not None:
        agent_cfg["disable_first_message_interruptions"] = disable_first_message_interruptions

    tts_cfg = dict(DEFAULT_TTS_CONFIG)
    if voice_id:
        tts_cfg["voice_id"] = voice_id
    if model_id:
        tts_cfg["model_id"] = model_id

    payload: dict[str, Any] = {
        "conversation_config": {
            "agent": agent_cfg,
            "tts": tts_cfg,
            "turn": dict(DEFAULT_TURN_CONFIG),
        }
    }
    if agent_name:
        payload["name"] = agent_name
    return payload

