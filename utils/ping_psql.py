# ping_postgres.py
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def main():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not defined in .env")
        sys.exit(1)

    try:
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5},  # psycopg2
            future=True,
        )
        with engine.connect() as conn:
            val = conn.execute(text("SELECT 1")).scalar()
        if val == 1:
            print("✅ Postgres OK (SELECT 1)")
            sys.exit(0)
        else:
            print("❌ Postgres responded unexpectedly")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to connect to Postgres: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
