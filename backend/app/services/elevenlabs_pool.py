"""ElevenLabs Dual-Account Failover & Credit Monitoring Service.

Maintains real-time quota tracking across Primary and Backup ElevenLabs accounts.
Automatically switches to the Backup account if Primary credits fall below
ELEVENLABS_MIN_CHARACTERS_THRESHOLD (or if Primary returns 401/429/quota errors).
"""

import time
import logging
from typing import Any, Dict, Optional
import httpx
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Cache store: { "primary": (timestamp, data), "backup": (timestamp, data) }
_QUOTA_CACHE: Dict[str, tuple[float, Dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 60.0  # Check subscription at most once per minute


async def _fetch_subscription(api_key: str) -> Dict[str, Any]:
    """Query ElevenLabs subscription endpoint to get current character balance."""
    if not api_key:
        return {"is_healthy": False, "error": "No API key provided", "remaining": 0}

    url = "https://api.elevenlabs.io/v1/user/subscription"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers={"xi-api-key": api_key})
            if resp.status_code == 200:
                data = resp.json()
                count = data.get("character_count", 0)
                limit = data.get("character_limit", 0)
                remaining = max(0, limit - count)
                return {
                    "is_healthy": True,
                    "character_count": count,
                    "character_limit": limit,
                    "remaining": remaining,
                    "tier": data.get("tier", "unknown"),
                    "status": data.get("status", "active"),
                }
            elif resp.status_code in (401, 403):
                logger.warning(f"ElevenLabs API authentication failure: {resp.status_code}")
                return {"is_healthy": False, "error": "Authentication failed", "remaining": 0}
            elif resp.status_code == 429:
                logger.warning("ElevenLabs API rate limit / quota exceeded (429)")
                return {"is_healthy": False, "error": "Quota or rate limit exceeded", "remaining": 0}
            else:
                logger.warning(f"ElevenLabs subscription check returned {resp.status_code}")
                return {"is_healthy": False, "error": f"HTTP {resp.status_code}", "remaining": 0}
    except Exception as e:
        logger.error(f"Error checking ElevenLabs subscription: {e}")
        return {"is_healthy": False, "error": str(e), "remaining": 0}


async def get_account_status(account: str = "primary", force_refresh: bool = False) -> Dict[str, Any]:
    """Retrieve quota status for an account ('primary' or 'backup') with TTL caching."""
    now = time.time()
    cached = _QUOTA_CACHE.get(account)
    if not force_refresh and cached and (now - cached[0] < CACHE_TTL_SECONDS):
        return cached[1]

    api_key = settings.ELEVENLABS_API_KEY if account == "primary" else settings.ELEVENLABS_API_KEY_BACKUP
    status = await _fetch_subscription(api_key)
    _QUOTA_CACHE[account] = (now, status)
    return status


async def get_active_agent_credentials() -> Dict[str, Any]:
    """Select the active ElevenLabs Agent credentials based on credit health.
    
    Returns:
        dict with keys: 'account', 'agent_id', 'api_key', 'is_backup', 'remaining', 'threshold'
    """
    threshold = settings.ELEVENLABS_MIN_CHARACTERS_THRESHOLD

    # 1. Check Primary Account
    primary_status = await get_account_status("primary")
    primary_agent = settings.ELEVENLABS_AGENT_ID or "agent_6201m7ajf2jbeztrpae3xhw418np"
    primary_remaining = primary_status.get("remaining", 0)

    # If Primary has sufficient credits, use it
    if primary_status.get("is_healthy", False) and primary_remaining > threshold:
        return {
            "account": "primary",
            "agent_id": primary_agent,
            "api_key": settings.ELEVENLABS_API_KEY,
            "is_backup": False,
            "remaining": primary_remaining,
            "threshold": threshold,
            "character_count": primary_status.get("character_count", 0),
            "character_limit": primary_status.get("character_limit", 10000),
        }

    # 2. Primary has low credits or is unavailable -> Check Backup Account
    backup_agent = settings.ELEVENLABS_AGENT_ID_BACKUP or "agent_0901m79nh3fcfhj9yn7f6ktqggfx"
    backup_key = settings.ELEVENLABS_API_KEY_BACKUP

    if backup_key:
        backup_status = await get_account_status("backup")
        backup_remaining = backup_status.get("remaining", 0)

        if backup_status.get("is_healthy", False) and backup_remaining > 0:
            logger.warning(
                f"⚠️ ElevenLabs Failover Activated: Primary has {primary_remaining} credits (threshold: {threshold}). "
                f"Routing call/session to Backup Agent ({backup_agent}) with {backup_remaining} credits."
            )
            return {
                "account": "backup",
                "agent_id": backup_agent,
                "api_key": backup_key,
                "is_backup": True,
                "remaining": backup_remaining,
                "threshold": threshold,
                "character_count": backup_status.get("character_count", 0),
                "character_limit": backup_status.get("character_limit", 10000),
                "failover_reason": primary_status.get("error") or f"Primary credits ({primary_remaining}) below threshold ({threshold})"
            }

    # If Backup is not configured or also failed, fall back to Primary with whatever remaining
    return {
        "account": "primary",
        "agent_id": primary_agent,
        "api_key": settings.ELEVENLABS_API_KEY,
        "is_backup": False,
        "remaining": primary_remaining,
        "threshold": threshold,
        "character_count": primary_status.get("character_count", 0),
        "character_limit": primary_status.get("character_limit", 10000),
    }


async def get_pool_status() -> Dict[str, Any]:
    """Return status summary for both Primary and Backup accounts."""
    primary = await get_account_status("primary")
    backup = await get_account_status("backup")
    active = await get_active_agent_credentials()

    return {
        "active_account": active.get("account"),
        "active_agent_id": active.get("agent_id"),
        "is_failover_active": active.get("is_backup", False),
        "primary": {
            "configured": bool(settings.ELEVENLABS_API_KEY),
            "agent_id": settings.ELEVENLABS_AGENT_ID or "agent_6201m7ajf2jbeztrpae3xhw418np",
            **primary,
        },
        "backup": {
            "configured": bool(settings.ELEVENLABS_API_KEY_BACKUP),
            "agent_id": settings.ELEVENLABS_AGENT_ID_BACKUP or "agent_0901m79nh3fcfhj9yn7f6ktqggfx",
            **backup,
        },
    }
