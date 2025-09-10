# tests/test_workflows.py
from pprint import pprint
import requests
from typing import Optional, Dict, Any

from app.workflows.guardrails_session import run_guardrails_session
from app.utils.triggers import execute_workflow
from app.workflows.guardrails_runner import handle_user_message

HEALTH_URL = "http://127.0.0.1:9000/health"


# ----------------------------
# Helpers
# ----------------------------
def _ping_health(url: str = HEALTH_URL) -> bool:
    try:
        r = requests.get(url, timeout=3)
        print(f"[PING] {url} -> {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"[PING] Failed: {e}")
        return False


def _run_guardrails_only(text: str, user_id: str = "u123", session_id: str = "s123",
                         context: Optional[Dict[str, Any]] = None):
    print("\n[TEST] Guardrails → intent")
    res = run_guardrails_session(text, user_id=user_id, session_id=session_id, context=context or {"source": "tests"})
    pprint(res)
    return res


def _run_trigger(intent: str, text: str, user_id: str = "u123", session_id: str = "s123",
                 context: Optional[Dict[str, Any]] = None):
    print("\n[TEST] Trigger → corresponding agent")
    resp = execute_workflow(intent, user_text=text, context=context or {"user_id": user_id},
                            user_id=user_id, session_id=session_id)
    pprint(resp)
    return resp


def _run_full_flow(text: str, user_id: str = "u123", session_id: str = "s123",
                   context: Optional[Dict[str, Any]] = None):
    print("\n[TEST] Full flow Guardrails → Trigger")
    out = handle_user_message(text, context=context or {"user_id": user_id}, user_id=user_id, session_id=session_id)
    pprint(out)
    return out


# ----------------------------
# Tests (pytest)
# ----------------------------
def test_guardrails_ok():
    assert _ping_health(), "API is not up at http://127.0.0.1:9000/health"
    text = "I just want to talk about programming."
    res = _run_guardrails_only(text)
    assert res.allowed is True
    assert res.intent == "normal_session"


def test_trigger_ok():
    assert _ping_health(), "API is not up at http://127.0.0.1:9000/health"
    text = "I just want to talk about programming."
    resp = _run_trigger("normal_session", text)
    assert resp["status"] == "ok"
    assert resp["workflow"] == "normal_session"


def test_full_flow_ok():
    assert _ping_health(), "API is not up at http://127.0.0.1:9000/health"
    text = "I just want to talk about programming."
    out = _run_full_flow(text)
    assert out["final"]["status"] == "ok"
    assert out["guardrails"]["intent"] == "normal_session"


# ----------------------------
# Interactive execution (python -m tests.test_workflows)
# ----------------------------
if __name__ == "__main__":
    print("=== Interactive mode: Guardrails → Trigger ===")
    if not _ping_health():
        print("❌ API is not available. Start the server: uvicorn main:app --reload --port 9000")
        raise SystemExit(1)

    question = input("\nType your question: ").strip()
    if not question:
        print("Nothing typed. Exiting.")
        raise SystemExit(0)

    # 1) Guardrails
    gr = _run_guardrails_only(question)

    # 2) If blocked, exit
    if not gr.allowed or not gr.intent:
        print("\n[FINAL] BLOCKED by guardrails.")
        raise SystemExit(0)

    # 3) Trigger (routes the intent to the agent)
    trig = _run_trigger(gr.intent, question)

    # 4) Full flow (just to demonstrate integrated orchestration)
    full = _run_full_flow(question)

    print("\n✅ End of interactive flow.")
