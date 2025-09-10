# app/session_context.py
import json
from app.redis_client import get_redis_client

WINDOW_SIZE = 20
TTL_SECONDS = 1800

def save_message(user_id, text, role):
    r = get_redis_client()
    key = f"session:{user_id}"
    msg = {"role": role, "text": text}
    r.rpush(key, json.dumps(msg))
    r.ltrim(key, -WINDOW_SIZE, -1)
    r.expire(key, TTL_SECONDS)

def get_context(user_id):
    r = get_redis_client()
    key = f"session:{user_id}"
    msgs = r.lrange(key, 0, -1)
    return [json.loads(m) for m in msgs]

def build_prompt(user_id):
    context = get_context(user_id)
    prompt = ""
    for msg in context:
        role = "User" if msg['role'] == "user" else "Agent"
        prompt += f"{role}: {msg['text']}\n"
    return prompt.strip()
