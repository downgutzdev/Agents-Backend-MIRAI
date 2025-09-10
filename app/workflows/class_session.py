# app/workflows/class_session.py

from __future__ import annotations

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure Python sees the project root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from config import AGENT_URLS
from app.models.sessao_aluno import SessaoAluno
from app.utils.session_store import (
    save_session_message,
    get_session_history,
    clear_session,
)

# =========================
# DB config
# =========================
DATABASE_URL = os.getenv("DATABASE_URL")

# =========================
# HTTP session with Retry/Backoff
# =========================
_session = requests.Session()
_retry = Retry(
    total=5,
    connect=3,
    read=3,
    backoff_factor=1.5,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset(["POST", "GET"]),
)
_adapter = HTTPAdapter(max_retries=_retry)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)


def call_agent(url: str, payload: dict, timeout: Tuple[int, int] = (10, 120)) -> Dict[str, Any]:
    """
    Resilient HTTP call:
      - Retry with backoff for 429/5xx and timeouts
      - Timeout is a tuple: (connect, read)
      - Logs raw response when not JSON-parseable
    """
    print(f"\n[DEBUG] Calling agent {url} with payload:")
    try:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    except Exception:
        print(payload)

    try:
        resp = _session.post(url, json=payload, timeout=timeout)
    except requests.exceptions.ReadTimeout:
        print(f"[ERROR] ReadTimeout on {url} (timeout={timeout}).")
        raise
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network failure when calling {url}: {e}")
        raise

    try:
        resp.raise_for_status()
    except requests.HTTPError:
        print(f"[DEBUG] HTTP {resp.status_code} body:")
        print(resp.text[:2000])
        raise

    try:
        return resp.json()
    except ValueError:
        print("[WARN] Response is not JSON. Raw body:")
        print(resp.text[:2000])
        return {"raw": resp.text}


# =========================
# Session / batching helpers
# =========================

def _user_only_text(history: List[Dict[str, Any]]) -> str:
    """
    Extract only USER UTTERANCES from the history (less noise for schema_creator).
    """
    parts: List[str] = []
    for m in history:
        role = (m.get("role") or "").lower()
        content = (m.get("content") or "").strip()
        if role == "user" and content:
            parts.append(content)
    return "\n".join(parts)


def _chunk_text(s: str, max_chars: int) -> List[str]:
    """
    Slice string into chunks of up to max_chars.
    Simple and robust (does not rely on sentence boundaries).
    """
    s = s or ""
    if not s:
        return []
    chunks = []
    i = 0
    n = len(s)
    while i < n:
        chunks.append(s[i : i + max_chars])
        i += max_chars
    return chunks


def _schema_eval_batch(batch_text: str) -> Dict[str, str]:
    """
    Sends ONE batch to schema_creator and returns a dict with guaranteed keys.
    Uses quick local retries (in addition to requests' Retry).
    """
    if "schema_creator" not in AGENT_URLS:
        raise KeyError(
            "AGENT_URLS['schema_creator'] missing. Add in config.py: "
            "AGENT_URLS['schema_creator'] = f'{BASE_URL}/mirai_agents/schema_creator/ask'"
        )

    payload = {
        "question": batch_text,
        "model_name": "gemini-1.5-flash",
        "temperature": 0.2,
    }

    # light local attempts
    last_err = None
    for attempt in range(1, 3):  # 2 local attempts
        try:
            resp = call_agent(AGENT_URLS["schema_creator"], payload)
            # Standardized API from the new router: returns direct keys
            strong = (resp.get("strong_points") or "").strip()
            weak = (resp.get("weak_points") or "").strip()
            general = (resp.get("general_comments") or "").strip()
            return {"strong_points": strong, "weak_points": weak, "general_comments": general}
        except requests.HTTPError as e:
            print(
                f"[WARN] 502/5xx on {AGENT_URLS['schema_creator']}. "
                f"Attempt {attempt}/2. Waiting {2**attempt:.1f}s…"
            )
            time.sleep(2**attempt)
            last_err = e
        except requests.RequestException as e:
            print(
                f"[WARN] Network error on {AGENT_URLS['schema_creator']} ({e}). "
                f"Attempt {attempt}/2. Waiting {2**attempt:.1f}s…"
            )
            time.sleep(2**attempt)
            last_err = e

    # batch fallback: empty (does not interrupt the whole session)
    print(f"[ERROR] schema_creator failed on batch: {last_err} — using empty placeholders.")
    return {"strong_points": "", "weak_points": "", "general_comments": ""}


def _aggregate_evals(evals: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Merge lists of strengths/weaknesses/comments across batches.
    Remove empties, simple dedup, and limit length.
    """
    def _join_unique(keys_vals: List[str], max_len: int = 2000) -> str:
        seen = set()
        out = []
        for x in keys_vals:
            x = (x or "").strip()
            if not x:
                continue
            if x in seen:
                continue
            seen.add(x)
            out.append(x)
        agg = " • ".join(out)
        return agg[:max_len]

    strengths = _join_unique([e.get("strong_points", "") for e in evals])
    weaknesses = _join_unique([e.get("weak_points", "") for e in evals])
    comments = _join_unique([e.get("general_comments", "") for e in evals], max_len=4000)
    return {"strong_points": strengths, "weak_points": weaknesses, "general_comments": comments}


# =========================
# Session flows
# =========================

def run_class_session(aluno_uuid: str, question: str, session_id: str) -> Dict[str, Any]:
    """
    “Online” study session:
      - Saves the question in Redis
      - Requests a LITE PLAN from the Planner (ultra-compact) to reduce cost/latency
      - Calls Teacher with that plan
      - Saves responses in Redis (no Postgres persistence yet)
    """
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # 1) User message
        save_session_message(session_id, role="user", content=question)

        # 2) Planner LITE (less work): 5–7 bullets, max ~120–150 words
        #    we pass the instruction in the planner's "question" (its prompt uses this field)
        planner_question = (
            "Generate an ULTRA-COMPACT lesson plan (max ~120–150 words) in 5–7 bullets. "
            "Focus on objectives, essential topics, practical activity, and comprehension check. "
            "Avoid long text; keep bullets short."
        )
        planner_payload = {
            "question": planner_question,
            "tema": "Aula personalizada",
            "context_schema": f"Última pergunta do aluno: {question}",
            "model_name": "gemini-1.5-flash",
            "temperature": 0.2,
        }
        planner_resp = call_agent(AGENT_URLS["planner"], planner_payload)
        plan_text = planner_resp.get("plan") if isinstance(planner_resp, dict) else str(planner_resp)

        save_session_message(session_id, role="agent", content=f"[PLANO LITE]\n{plan_text}")

        # 3) Teacher with LITE plan
        teacher_payload = {
            "question": question,
            "plan": plan_text or "Plano enxuto: objetivos, tópicos, prática, checagem.",
            "context_schema": "Contexto mínimo; adaptar ao aluno.",
            "model_name": "gemini-1.5-flash",
            "temperature": 0.4,
        }
        teacher_resp = call_agent(AGENT_URLS["professor"], teacher_payload)
        teacher_text = teacher_resp.get("lesson") if isinstance(teacher_resp, dict) else str(teacher_resp)
        save_session_message(session_id, role="agent", content=f"[PROFESSOR]\n{teacher_text}")

        return {"status": "ok", "planner": {"plan": plan_text}, "professor": {"lesson": teacher_text}}

    finally:
        db.close()


def finalize_session_with_plan(aluno_uuid: str, session_id: str) -> Dict[str, Any]:
    """
    End of session:
      - Retrieves history from Redis
      - Sends ONLY USER UTTERANCES to schema_creator in BATCHES
      - Aggregates strong/weak/general
      - Calls COMPACT Planner (also lean)
      - Persists to Postgres
      - Clears Redis
    """
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        history = get_session_history(session_id)
        if not history:
            raise ValueError("No history found for this session.")

        # 1) Only user utterances
        user_only = _user_only_text(history)
        total_chars = len(user_only)
        if total_chars == 0:
            # ensure there is always something for schema_creator
            user_only = "No user utterances recorded in this session."
        print(f"[DEBUG] Total chars (user-only)={len(user_only)}")

        # 2) Batches to schema_creator
        BATCH = 1800
        chunks = _chunk_text(user_only, BATCH)
        print(f"[DEBUG] Batches={len(chunks)} | batch_size={BATCH}")
        evals: List[Dict[str, str]] = []
        for idx, ch in enumerate(chunks, start=1):
            print(f"[DEBUG] Evaluating batch {idx}/{len(chunks)} | len={len(ch)}")
            eval_result = _schema_eval_batch(ch)
            evals.append(eval_result)

        avaliacao = _aggregate_evals(evals)

        # 3) COMPACT Planner (less work)
        planner_question = (
            "Based on the student's points below, generate a COMPACT PLAN (max ~150–200 words) "
            "in short bullets (5–8 items), including: 1) objectives, 2) essential topics, "
            "3) practical activity, 4) simple evaluation, 5) next steps."
        )
        compact_context = (
            f"Pontos fortes: {avaliacao.get('strong_points','')}\n"
            f"Pontos fracos: {avaliacao.get('weak_points','')}\n"
            f"Observações: {avaliacao.get('general_comments','')}"
        )
        planner_payload = {
            "question": planner_question,
            "tema": "Plano consolidado da sessão",
            "context_schema": compact_context[:6000],  # avoid huge payloads
            "model_name": "gemini-1.5-flash",
            "temperature": 0.2,
        }
        planner_resp = call_agent(AGENT_URLS["planner"], planner_payload)
        plan_text = planner_resp.get("plan") if isinstance(planner_resp, dict) else str(planner_resp)

        # 4) Persist to DB
        SessionCls = sessionmaker(bind=engine)
        db = SessionCls()
        nova_sessao = SessaoAluno(
            id_estudante=aluno_uuid,
            strong_points=avaliacao.get("strong_points") or None,
            weak_points=avaliacao.get("weak_points") or None,
            general_comments=avaliacao.get("general_comments") or None,
            tema=plan_text or "Plano compacto gerado",
        )
        db.add(nova_sessao)
        db.commit()
        db.refresh(nova_sessao)

        # 5) Clear Redis
        clear_session(session_id)

        return {
            "status": "finalizado",
            "sessao_uuid": str(nova_sessao.uuid),
            "avaliacao": avaliacao,
            "plano": plan_text,
        }

    finally:
        db.close()


# =========================
# Direct execution (CLI)
# =========================

if __name__ == "__main__":
    aluno_uuid = "88888888-8888-8888-8888-888888888888"  # adjust for your student
    session_id = "sessao_teste"

    pergunta = input("Type the student's question: ").strip() or "Bom dia"

    print("\n[▶️] Running session...\n")
    try:
        resultado = run_class_session(aluno_uuid, pergunta, session_id)
        print(resultado)
    except Exception as e:
        print(f"[ERROR] Failed to run workflow (online phase): {e}")

    finalizar = input("\nFinalize session? (s/n): ").strip().lower()
    if finalizar == "s":
        try:
            resultado_final = finalize_session_with_plan(aluno_uuid, session_id)
            print("\n--- SESSION FINALIZED ---")
            print(json.dumps(resultado_final, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"[ERROR] Failed to finalize session: {e}")
