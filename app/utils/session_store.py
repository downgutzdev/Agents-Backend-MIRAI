import os
import json
import redis
from urllib.parse import urlparse
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Get REDIS_URL from environment (ex: redis://:password@localhost:6379/0)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Parse the URL
url = urlparse(REDIS_URL)

redis_client = redis.Redis(
    host=url.hostname,
    port=url.port or 6379,
    db=int(url.path.replace("/", "")) if url.path else 0,
    username=url.username,
    password=url.password,
    decode_responses=True
)


def save_session_message(session_id: str, role: str, content: str, extra: Dict[str, Any] | None = None) -> None:
    """
    Save a message into Redis.
    Args:
        session_id: session identifier (e.g., student UUID or unique session UUID)
        role: 'user' or 'agent'
        content: message text
        extra: optional metadata (dict)
    """
    key = f"session:{session_id}"
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "role": role,
        "content": content,
        "extra": extra or {}
    }
    redis_client.rpush(key, json.dumps(entry))


def get_session_history(session_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve the entire history of a session from Redis.
    """
    key = f"session:{session_id}"
    messages = redis_client.lrange(key, 0, -1)
    return [json.loads(m) for m in messages]


def clear_session(session_id: str) -> None:
    """
    Remove the entire history of a session in Redis.
    """
    key = f"session:{session_id}"
    redis_client.delete(key)
