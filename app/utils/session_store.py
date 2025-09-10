import os
import json
import redis
from urllib.parse import urlparse
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# pega REDIS_URL do ambiente (ex: redis://:senha@localhost:6379/0)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# parse da URL
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
    Salva uma mensagem no Redis.
    Args:
        session_id: identificador da sessão (ex: uuid do aluno ou uuid único da sessão)
        role: 'user' ou 'agent'
        content: mensagem em texto
        extra: metadados opcionais (dict)
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
    Recupera todo o histórico de uma sessão do Redis.
    """
    key = f"session:{session_id}"
    messages = redis_client.lrange(key, 0, -1)
    return [json.loads(m) for m in messages]


def clear_session(session_id: str) -> None:
    """
    Remove todo o histórico de uma sessão no Redis.
    """
    key = f"session:{session_id}"
    redis_client.delete(key)
