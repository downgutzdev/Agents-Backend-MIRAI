# app/redis_client.py
import os
import redis
from dotenv import load_dotenv

load_dotenv()

# Using single URL (redis:// or rediss://)
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise RuntimeError("REDIS_URL not defined in .env")

# Singleton
_redis_instance = None

def get_redis_client():
    global _redis_instance
    if _redis_instance is None:
        _redis_instance = redis.from_url(
            REDIS_URL,
            decode_responses=True,   # strings instead of bytes
        )
    return _redis_instance
