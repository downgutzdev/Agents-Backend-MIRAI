from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import requests
from config import AGENT_URLS
import os

DATABASE_URL = os.getenv("DATABASE_URL")


def ping_db():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[OK] Database connection established.")
        return engine
    except Exception as e:
        print(f"[ERROR][1] Failed to connect to the database: {e}")
        exit(1)


def check_table_exists(engine):
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT to_regclass('public.sessao_aluno')"))
            if result is None:
                raise Exception("Table 'sessao_aluno' not found in the database.")
        print("[OK] Table 'sessao_aluno' found.")
    except Exception as e:
        print(f"[ERROR][2] Failed to access table 'sessao_aluno': {e}")
        exit(2)


def get_last_sessao_aluno(engine, aluno_uuid: str):
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                SELECT strong_points, weak_points, general_comments, created_at
                FROM sessao_aluno
                WHERE id_estudante = :aluno_uuid
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"aluno_uuid": aluno_uuid}
        ).fetchone()
        if not result:
            raise ValueError("No data found for the student.")
        contexto = (
            f"Strong points: {result.strong_points}\n"
            f"Weak points: {result.weak_points}\n"
            f"General comments: {result.general_comments}\n"
            f"(Session recorded at: {result.created_at})"
        )
        print("[OK] Data fetched from database.")
        return contexto
    except Exception as e:
        print(f"[ERROR][3] Failed to fetch student data: {e}")
        exit(3)
    finally:
        db.close()


def gerar_plano_aula(contexto_aluno: str, model_name: str = "gemini-2.5-pro"):
    url = AGENT_URLS["planner"]  # uses centralized endpoint
    payload = {
        "question": contexto_aluno,
        "model_name": model_name
    }
    resp = requests.post(url, json=payload, timeout=30)
    if not resp.ok:
        raise Exception(f"Error when calling Planner: {resp.status_code} {resp.text}")
    return resp.json().get("plan", resp.text)


if __name__ == "__main__":
    # 1. Test DB connection
    engine = ping_db()

    # 2. Check if table is accessible
    check_table_exists(engine)

    # 3. Fetch student data
    id_estudante = input("Enter the student's UUID: ").strip()
    contexto_aluno = get_last_sessao_aluno(engine, id_estudante)
    print("\nContext extracted from database:\n")
    print(contexto_aluno)

    print("\nCalling Planner Agent...")
    try:
        plano = gerar_plano_aula(contexto_aluno)
        print("\n--- PERSONALIZED LESSON PLAN ---\n")
        print(plano)
    except Exception as e:
        print(f"[ERROR][4] Failed to call Planner Agent: {e}")
