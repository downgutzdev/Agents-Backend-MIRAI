# ping_redis.py
import os
import sys
import redis
from dotenv import load_dotenv

def main():
    load_dotenv()
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        print("❌ REDIS_URL not defined in .env")
        sys.exit(1)

    try:
        r = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=5)
        ok = r.ping()
        if ok:
            print("✅ Redis OK (PING)")
            sys.exit(0)
        else:
            print("❌ Redis responded False on PING")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
